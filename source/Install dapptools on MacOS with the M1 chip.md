### How to install dapptools on MacOS with the M1 chip

*At least until there's actual support from NixOS for the new M1 chip...*

The Ethereum [dapptools](https://dapp.tools/) suite relies on the [NixOS](https://nixos.org/) package management system. Installation was pretty simple in previous architectures, but if you find yourself with a new Mac with the [M1 chip](https://www.apple.com/newsroom/2021/10/introducing-m1-pro-and-m1-max-the-most-powerful-chips-apple-has-ever-built/), there is an extra step.

NixOS is the prerequisite, so you need to install that first. Using a terminal, do

```
# You must be a sudoer
curl -L https://nixos.org/nix/install | sh

# Run this or login again to use Nix
. "$HOME/.nix-profile/etc/profile.d/nix.sh"
```

Now, **before** trying to install `dapptools`, you need to edit `/etc/nix/nix.conf` and add the following line, if it doesn't exist:

```
system = x86_64-darwin
```

This tells NixOS to use the old Intel architecture (via [Rosetta](https://developer.apple.com/documentation/apple-silicon/about-the-rosetta-translation-environment)) for its packages.

Note you will need to edit `/etc/nix/nix.conf` via `sudo`.

After you've done this, you should be good to go to install `dapptools`:

```
curl https://dapp.tools/install | sh
```