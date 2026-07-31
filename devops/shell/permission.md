# Permission of file in Bash

## check file/directory permission
```shell
ls -l
# -rwxr-xr-x 1 root root 920788 Mar 28 2013 bash
```

The first block (-rwxr-xr-x) means that

- the first character signifies the type of file. '-' for file and 'd' for directory 'l' for a link.
- It is readable, writeable and executable by the user (the first triple rwx)
- It is readable and executable by the group (the second triple r-x)
- It is readable and executable by anyone (the third triple r-x)
The next is that the file is ownded by the user root (the first root) and the group root (the second root).

The 1 means, number of links created for this file.

Then the file size is printed (920788 bytes in this case).

Then the creation date of the file (in this case Mar 28 2013) is printed. This could also be formated like Mar 28 08:15 if the year is the current year.

At last the name of the file (bash in this case) is printed.


## chown
> change file or directory owner & group
```shell
# -R change owner recursively.
chown -R phil:allusers /home/user
```

## chmod
> change file access permssion
```shell
# make private key file only accessible for owner.
chmod 600 ~/.ssh/id_rsd
```


> references
- https://unix.stackexchange.com/questions/200503/what-does-the-output-of-ls-l-mean