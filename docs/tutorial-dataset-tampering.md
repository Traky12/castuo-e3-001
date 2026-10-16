# Tutorial: detect dataset tampering end to end

This walkthrough creates a small synthetic CSV dataset, signs its manifest with two Ed25519 keys, verifies it against pinned public keys, and then checks three independent mutations: editing a value, adding a file, and deleting a file.

**Scope:** this is an example of file-integrity and configured-signature verification. The sample data is synthetic. A passing result does not prove that a dataset is true, that it was collected correctly, that two signers are independent people, or that a real-world identity has been established.

## 1. Prerequisites and source setup

- Python 3.11 or newer.
- Git.
- An environment that can install the project and its dependencies. Setup may need network access; once installed, e3bundle's verification command performs no network requests.
- Use a disposable workspace. The private signing keys and the generated dataset will be kept **outside the cloned repository** so they are not accidentally committed.

The public PyPI distribution and the live browser demo have separate release gates. This tutorial installs the working tree from source; it does not claim that PyPI or Pages has been unblocked.

~~~bash
git clone https://github.com/Traky12/castuo-e3-001.git
cd castuo-e3-001
git rev-parse HEAD
python -m venv .venv
~~~

Activate the virtual environment and install the project locally.

**Bash / Zsh**

~~~bash
source .venv/bin/activate
python -m pip install .
~~~

**PowerShell**

~~~powershell
.\.venv\Scripts\Activate.ps1
python -m pip install .
~~~

Create a sibling workspace and move into it. All following commands are run from this workspace, not from the Git checkout.

**Bash / Zsh**

~~~bash
mkdir -p ../e3bundle-tutorial-workspace
cd ../e3bundle-tutorial-workspace
~~~

**PowerShell**

~~~powershell
New-Item -ItemType Directory -Force ..\e3bundle-tutorial-workspace | Out-Null
Set-Location ..\e3bundle-tutorial-workspace
~~~

## 2. Create a synthetic dataset and two signing keys

This single Python command creates two files in the bundle and a separate directory for private/public key material. It can be pasted into Bash/Zsh or PowerShell.

~~~bash
python -c 'from pathlib import Path; root=Path("dataset-bundle"); (root/"data").mkdir(parents=True, exist_ok=True); (root/"data/readings.csv").write_text("timestamp,temperature_c,plot\n2026-10-15T08:00:00Z,21.4,GH-01\n2026-10-15T09:00:00Z,21.7,GH-01\n", encoding="utf-8"); (root/"report.md").write_text("Synthetic tutorial data only; not field evidence.\n", encoding="utf-8"); Path("keys").mkdir(exist_ok=True)'
~~~

Generate two **different keys**. Keep the .key files secret and outside the bundle. The .pub.json files contain public keys.

~~~bash
e3bundle keygen --private-key keys/operator.key --signer-id operator
e3bundle keygen --private-key keys/reviewer.key --signer-id reviewer
~~~

Both keys are generated locally for this tutorial. Two keys are not proof of two independent people; for a real approval workflow, key custody, reviewer independence and the way public keys are pinned need separate governance.

## 3. Pin the public keys, then create and sign the manifest

Create a trust file from the generated public keys. This does not include either private key.

~~~bash
python -c 'import json; from pathlib import Path; ids=["operator","reviewer"]; data={i:json.loads((Path("keys")/f"{i}.pub.json").read_text(encoding="utf-8"))["public_key_b64"] for i in ids}; Path("trusted-keys.json").write_text(json.dumps(data, indent=2)+"\n", encoding="utf-8")'
~~~

Create the manifest **after** all data files are in place, then add both signatures over that exact manifest.

~~~bash
e3bundle manifest dataset-bundle --bundle-id tutorial-dataset-001
e3bundle sign dataset-bundle --private-key keys/operator.key --signer-id operator --role operator
e3bundle sign dataset-bundle --private-key keys/reviewer.key --signer-id reviewer --role reviewer
~~~

Expected: the manifest declares two files; signatures.json reports one signature from operator and one from reviewer. Do not modify the files and then regenerate the manifest during a tampering test: that would describe a different bundle instead of detecting the mutation.

## 4. Verify the original bundle

~~~bash
e3bundle verify dataset-bundle --min-signatures 2 --trusted-keys trusted-keys.json --strict --format text
~~~

Expected status and exit code:

~~~text
VERIFIED  tutorial-dataset-001  files 2/2  signatures 2 trusted / 2 valid
exit code: 0
~~~

The trusted-key file pins the public keys that count toward the threshold. The signature metadata's role is descriptive; it does not itself prove identity, independence or authority.

## 5. Create three isolated copies for negative tests

The following command is also portable across Bash/Zsh and PowerShell. Each mutation starts from the same signed baseline so the findings do not contaminate each other.

~~~bash
python -c 'import shutil; [shutil.copytree("dataset-bundle", name) for name in ("scenario-edit", "scenario-add", "scenario-delete")]'
~~~

### Case A — Edit one value

Change one temperature in the copied bundle.

~~~bash
python -c 'from pathlib import Path; p=Path("scenario-edit/data/readings.csv"); s=p.read_text(encoding="utf-8"); assert s.count("21.4")==1; p.write_text(s.replace("21.4","21.9"), encoding="utf-8")'
e3bundle verify scenario-edit --min-signatures 2 --trusted-keys trusted-keys.json --strict --format text
~~~

Expected finding: **hash mismatch: data/readings.csv**. Expected exit code: **1**.

### Case B — Add a file

Add a file that was not in the original manifest.

~~~bash
python -c 'from pathlib import Path; Path("scenario-add/data/extra.txt").write_text("Added after signing.\n", encoding="utf-8")'
e3bundle verify scenario-add --min-signatures 2 --trusted-keys trusted-keys.json --strict --format text
~~~

Expected finding: **undeclared file: data/extra.txt**. Expected exit code: **1**.

### Case C — Delete a file

Delete a file that the original manifest declares.

~~~bash
python -c 'from pathlib import Path; Path("scenario-delete/report.md").unlink()'
e3bundle verify scenario-delete --min-signatures 2 --trusted-keys trusted-keys.json --strict --format text
~~~

Expected finding: **missing file: report.md**. Expected exit code: **1**.

For each negative case, immediately inspect the exit status before running another command:

- Bash / Zsh: **echo $?**
- PowerShell: **$LASTEXITCODE**

The command's exit status must be **1** when verification reports FAILED. Exit code **2** means unreadable input or a usage/input error; it is not the expected result of these three mutations.

## 6. Interpreting the result

| Result | Meaning |
|---|---|
| VERIFIED, exit 0 | Declared files match the manifest and the configured threshold of distinct pinned keys signed that manifest. |
| FAILED, exit 1 | At least one declared file changed, a declared file is missing, an undeclared file is present, or another verification predicate failed. |
| ERROR, exit 2 | The bundle, manifest, trusted-key file or command input could not be used as provided. |

A VERIFIED result does **not** establish that the temperature readings are accurate, that the data came from a real field site, that signers are independent, or that an organisation legally approved the data. e3bundle checks integrity and the configured cryptographic policy. It does not supply a timestamp authority or key-revocation service.

## Reproducibility notes

- Record the Git commit printed by git rev-parse HEAD, Python version, operating system, exact commands, findings and exit codes in any reproduction report.
- Do not include private keys in the bundle, a pull request, an issue, a screenshot or a public artifact.
- The commands are covered by the repository's automated dataset-tampering regression test. The CI run is repeatable evidence for the automated test, not independent human validation.
- Report problems using the repository's [issue tracker](https://github.com/Traky12/castuo-e3-001/issues). Do not exchange or request stars for reports or help.
