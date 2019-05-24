# LibreBlogging
Ideas and issue status: https://miro.com/app/board/o9J_kxu6Y1o=/

The first basic functionality is there :)

## Usage

### Development
Use `docker-compose-dev.yml` to create an image and run a container for development on LibreBlogging:

```shell
docker-compose -f docker-compose-dev.yml up
```

This maps your current directory to /app in the container, so you have direct access.

### Use LibreBlogging
It's as simple as

```shell
docker-compose up
```

BUT: Make sure that,

* ... you fill up the required fields in the compose file, like:
  * The UID in the compose file to the UID of your user. Otherwise, there will surely be permission issues with your volumes.
  * VIRTUAL_HOST
  * LETSENCRYPT_HOST
  * LETSENCRYPT_EMAIL
* ... in ./htpasswd/ is a htpasswd file named after your VIRTUAL_HOST. The default login for localhost is `user: foo` and `pass: bar`
* ... at least the IPFS swarm port (default 4001) is publicly reachable and forwarded to your machine.

## Keep in mind

* IPFS does not push your content to the network. The integrated IPFS node in LibreBlogging serves your content to anyone requesting it (and those can then serve it as well to others).
  * That means, __LibreBlogging should be running 24/7 in order to guarantee availability of your content.__
* IPFS is in an early stage and often lookup times for IPNS records are long.
* Especially newly set up nodes might take a while until the IPNS link works.

## What is it about?

LibreBlogging is a hassle-free tool that enables you to set up a simple blog on [IPFS](https://ipfs.io) in no time. The benefits of publishing on IPFS are:

* Content is _not censorable_, as content is not hosted in a single place or by a company.
* _Economical_, as you don't need to spend much money on hosting. You just need a small node to run IPFS on.
* _Scalability_, as your content is cached and distributed also by other IPFS users that read your content.

However, from a content creators perspective there are certain things that make publishing on IPFS rather difficult in comparison to regular blogging platforms:

* Your content is not addressed using handy domains, but through hashes that look like this: `QmTPixNxp6y3iWs2i5BTcv6EzNsX3MaEty1Yys2Nm4W8JD`
* Every time you add or change content, you get a new or changed hash *sigh*
* If you want an immutable address for your blog for sharing you can have one, the [IPNS](https://ipfs.io/ipns/docs.ipfs.io/guides/concepts/ipns/) hash of your node. However, that's still a hash...
* Everytime your blog changes, your blog root will have a new hash that needs to be published to IPNS.

With LibreBlogging we try to come over these hassles and make it simple and easy to have a blog on IPFS while staying as decentralized as possible.

![](about.png)
