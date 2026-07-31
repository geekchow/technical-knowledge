#  How install multiple java version on M1 chip Mac

## install home brew on m1 chip.

- install homebrew
```shell
# need to work around the GFW
 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

- put the path into `~/.zshrc`
```shell
# /opt/homebrew is the arm64 binary default installation path.
export PATH="/opt/homebrew/bin/:$PATH"
```

## install `jenv`

https://www.jenv.be

```shell
brew install jenv
# activate jenv for zsh
echo 'export PATH="$HOME/.jenv/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(jenv init -)"' >> ~/.zshrc

```

## download JDK and install them.

## add versions to `jenv`
```shell
jenv add /Library/Java/JavaVirtualMachines/adoptopenjdk-8.jdk/Contents/Home
jenv add /Library/Java/JavaVirtualMachines/jdk-11.0.13.jdk/Contents/Home
jenv add /Library/Java/JavaVirtualMachines/jdk-17.0.1.jdk/Contents/Home
```

## 