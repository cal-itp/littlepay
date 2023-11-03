# Config directory

This is where your local configuraiton will live.

This README is tracked to avoid a Linux issue with Docker Compose mounting this directory into the devcontainer outside of the
working source tree.

If this directory does not exist, Docker creates it as the `root` user before mounting, meaning the devcontainer user cannot
write files here.
