
# INSTALL GIT

To install GIT in your development environment. You can follow these steps.

+ Download GIT via console.
`
[opc@jenkins-master 00_AUTOMATING_A_NETWORK_INVENTORY_WITH_PYTHON]$ sudo yum install git

[opc@jenkins-master 00_AUTOMATING_A_NETWORK_INVENTORY_WITH_PYTHON]$ git --version
`

# CONFIGURE GIT AND LOCAL MACHINE

You need to configure SSH KEY in your PC

+ Verify if you have the file id_rsa.pub

```bash
[opc@jenkins-master 00_AUTOMATING_A_NETWORK_INVENTORY_WITH_PYTHON]$ ls -al ~/.ssh
total 12
drwx------.  2 opc opc   48 Feb 28 01:03 .
drwx------. 27 opc opc 4096 Feb 28 06:29 ..
-rw-------.  1 opc opc  400 Jun 27  2022 authorized_keys
-rw-r--r--.  1 opc opc  881 Feb 28 01:31 known_hosts
```

Nota: THERE IS NOT A FILE id_rsa.pub

```bash
[opc@jenkins-master 00_AUTOMATING_A_NETWORK_INVENTORY_WITH_PYTHON]$ ssh-keygen
Generating public/private rsa key pair.
Enter file in which to save the key (/home/opc/.ssh/id_rsa): [enter]
Enter passphrase (empty for no passphrase): [enter]
Enter same passphrase again: [enter]
Your identification has been saved in /home/opc/.ssh/id_rsa.
Your public key has been saved in /home/opc/.ssh/id_rsa.pub.
The key fingerprint is:[enter]
SHA256:d34vpdY+/rfOiQSq7yoEl9L2FLOpxIR+MxSMO3n001I opc@jenkins-master
The key's randomart image is:

+---[RSA 3072]----+
|    +..          |
|   o = o E       |
|  . O o B        |
|   B % B .       |
|    X * S ...    |
|     o . ..o.   .|
|    .    .  ...+ |
|     .  .   ..*o+|
|      .o+o   ooOO|
+----[SHA256]-----+

[opc@jenkins-master 00_AUTOMATING_A_NETWORK_INVENTORY_WITH_PYTHON]$ ls -al ~/.ssh
total 20
drwx------.  2 opc opc   80 Feb 28 18:25 .
drwx------. 27 opc opc 4096 Feb 28 06:29 ..
-rw-------.  1 opc opc  400 Jun 27  2022 authorized_keys
-rw-------.  1 opc opc 2602 Feb 28 18:25 id_rsa
-rw-r--r--.  1 opc opc  572 Feb 28 18:25 id_rsa.pub
-rw-r--r--.  1 opc opc  881 Feb 28 01:31 known_hosts

[opc@jenkins-master 00_AUTOMATING_A_NETWORK_INVENTORY_WITH_PYTHON]$ cat ~/.ssh/id_rsa.pub

ssh-rsa eRau8T40vnH3uryhEkjsjSoNj8oL7X3ifZ5shlCo32U9yp+wt+b0yCry9Rv7wvNznG1e5+Kz/H+QEzOF9geiYZOekJ8KUXz8qsbPZRA7vdwZCAZxDU0XQaXzWGWjL765Yno+QCirg8EbZHSY9He3MhrzJmJy1zzCkIpY/XRR4xxxxxRqq5pLhYUJJrmRYLWe/yXgT99m5lSShyrh9OIc9Y7LyVpEqg8Q2CGE8HNS85IlsLghNEFHuzdYqN+lfp7yiOVbBFuDkHhMKTI7WIF7vufUZ3iS2bgy+E4mvj6O4d/Kgb8SroWNLMVrpnKoEPHEZYFQPKId6Yt4sYfgmQjHu!!!!CWr
```

# LOAD SSH KEY IN GIT HUB

+ Previously you need to create an account in [GitHub](https://github.com/)

![image](https://user-images.githubusercontent.com/38144008/222931055-fedeb975-ebdf-4b5f-9791-be3193b935c0.png)

+ You need to create an repository in th portal web https://github.com. 

# SYNCRONIZE THE LOCAL ENVIRONMENT WITH A PREVIOUSLY INSTALLED REPOSITORY

```bash
[opc@jenkins-master DEVNET]$ git clone git@github.com:ERICK-ZABALA/AUTOMATING-A-NETWORK-INVENTORY-WITH-PYTHON.git
Cloning into 'AUTOMATING-A-NETWORK-INVENTORY-WITH-PYTHON'...
warning: You appear to have cloned an empty repository.

[opc@jenkins-master DEVNET]$ ls
AUTOMATING-A-NETWORK-INVENTORY-WITH-PYTHON  

[opc@jenkins-master DEVNET]$ cd AUTOMATING-A-NETWORK-INVENTORY-WITH-PYTHON/

NOTA: Git, se utiliza el comando "git pull". Este comando combina dos acciones: "git fetch", que descarga los cambios más recientes en el repositorio local, y "git merge", que combina los cambios descargados con los cambios locales.

[opc@jenkins-master AUTOMATING-A-NETWORK-INVENTORY-WITH-PYTHON]$ git pull
Your configuration specifies to merge with the ref 'refs/heads/main'
from the remote, but no such ref was fetched.


[opc@jenkins-master AUTOMATING-A-NETWORK-INVENTORY-WITH-PYTHON]$ echo "# Test" >> README.md

[opc@jenkins-master AUTOMATING-A-NETWORK-INVENTORY-WITH-PYTHON]$ ls
README.md
[opc@jenkins-master AUTOMATING-A-NETWORK-INVENTORY-WITH-PYTHON]$ git add README.md 
[opc@jenkins-master AUTOMATING-A-NETWORK-INVENTORY-WITH-PYTHON]$ git commit -m "first commit"

[main (root-commit) 304a4ba] first commit
 Committer: Oracle Public Cloud User <opc@jenkins-master.sub06270359170.jenkinsvcn.oraclevcn.com>
Your name and email address were configured automatically based
on your username and hostname. Please check that they are accurate.
You can suppress this message by setting them explicitly. Run the
following command and follow the instructions in your editor to edit
your configuration file:

    git config --global --edit

After doing this, you may fix the identity used for this commit with:

    git commit --amend --reset-author

 1 file changed, 1 insertion(+)
 create mode 100644 README.md

[opc@jenkins-master AUTOMATING-A-NETWORK-INVENTORY-WITH-PYTHON]$ git status

On branch main
Your branch is based on 'origin/main', but the upstream is gone.
  (use "git branch --unset-upstream" to fixup)

nothing to commit, working tree clean

[opc@jenkins-master AUTOMATING-A-NETWORK-INVENTORY-WITH-PYTHON]$ git push
Enumerating objects: 3, done.
Counting objects: 100% (3/3), done.
Writing objects: 100% (3/3), 254 bytes | 254.00 KiB/s, done.
Total 3 (delta 0), reused 0 (delta 0), pack-reused 0
To github.com:ERICK-ZABALA/AUTOMATING-A-NETWORK-INVENTORY-WITH-PYTHON.git

 * [new branch]      main -> main
[opc@jenkins-master AUTOMATING-A-NETWORK-INVENTORY-WITH-PYTHON]$ ls

README.md
```

# ISSUES TS GIT - REPOSITORIO LOCAL

+NOTA: If you have issues with the git pull or git pull -Xtheirs. you should indicate where is allocated your public key in your environment.
```bash
[opc@jenkins-master AUTOMATING-A-NETWORK-INVENTORY-WITH-PYTHON]$ git config --global credential.helper store
[opc@jenkins-master AUTOMATING-A-NETWORK-INVENTORY-WITH-PYTHON]$ git remote set-url origin git@github.com:ERICK-ZABALA/AUTOMATING-A-NETWORK-INVENTORY-WITH-PYTHON.git
```
# CREATE A FILE CONFIG 
```bash
[opc@jenkins-master AUTOMATING-A-NETWORK-INVENTORY-WITH-PYTHON]$ sudo nano  ~/.ssh/config

File:config
Host github.com
    MACs hmac-sha2-512

[opc@jenkins-master AUTOMATING-A-NETWORK-INVENTORY-WITH-PYTHON]$ git config core.sshCommand "ssh -i ~/.ssh/id_rsa"
```

# TRY AGAIN...

`(inventory) [opc@jenkins-master AUTOMATING-A-NETWORK-INVENTORY-WITH-PYTHON]$ git pull -Xtheirs`

# UPDATE REPOSITORY LOCAL FROM REPOSITORY GITHUB

The git pull command with the -Xtheirs option specifies the strategy for resolving conflicts during the merge process.

When Git encounters conflicts between the changes made in the local branch and the changes made in the remote branch, it tries to merge the changes automatically. However, if the changes conflict with each other, Git will not be able to automatically resolve the conflicts and will require manual intervention.

The -Xtheirs option tells Git to automatically resolve the conflicts by always choosing the changes from the remote branch. This means that if there are conflicts, Git will overwrite the local changes with the changes from the remote branch, without prompting for manual intervention.

In other words, git pull -Xtheirs is a command to fetch and merge changes from the remote branch, and automatically resolve conflicts in favor of the remote branch.

It's worth noting that this option should be used with caution, as it can potentially overwrite important changes made in the local branch. It's always a good practice to review and resolve conflicts manually, to ensure that the changes are applied correctly.

```bash
(inventory) [opc@jenkins-master AUTOMATING-A-NETWORK-INVENTORY-WITH-PYTHON]$ git pull -Xtheirs

remote: Enumerating objects: 5, done.
remote: Counting objects: 100% (5/5), done.
remote: Compressing objects: 100% (3/3), done.
remote: Total 3 (delta 1), reused 0 (delta 0), pack-reused 0
Unpacking objects: 100% (3/3), 815 bytes | 407.00 KiB/s, done.
From github.com:ERICK-ZABALA/AUTOMATING-A-NETWORK-INVENTORY-WITH-PYTHON
   add9a82..dd9651b  main       -> origin/main
Updating add9a82..dd9651b
Fast-forward
 README.md | 3 +++
 1 file changed, 3 insertions(+)

(inventory) [opc@jenkins-master AUTOMATING-A-NETWORK-INVENTORY-WITH-PYTHON]$ git status
On branch main
Your branch is up to date with 'origin/main'.

nothing to commit, working tree clean

(inventory) [opc@jenkins-master AUTOMATING-A-NETWORK-INVENTORY-WITH-PYTHON]$ git push
Everything up-to-date

```bash

