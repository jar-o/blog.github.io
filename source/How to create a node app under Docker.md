# How to create a node app under Docker

Want to run a Node-based app under Docker? It's a great way to create and distribute a Node application with only a single dependency: Docker. Users won't need to have `node` or `npm` anywhere on their system.

Let's start with the app itself. Just a basic *hello world* with dependencies. Create a file named `app.js`:

```
var figlet = require('figlet');

figlet('helowrld', function(err, data) {
    if (err) {
        console.log('Something went wrong...');
        console.dir(err);
        return;
    }
    console.log(data)
});
```

We're going to use the [figlet](https://www.npmjs.com/package/figlet) module to print out a nice ASCII-art style message. (Obviously to develop and test on your own system, you'll need to have `node` etc installed. It's simply not a requirement for users.)

Once your app is how you want it, you will now want to package it via Docker. Before we can get to creating a `Dockerfile` however, we'll need to create a file that `npm` can use to install your app. In the same folder as `app.js` create a file named `package.json`. It should look something like:

```
{
 "name": "helowrld",
 "version": "1.0.0",
 "description": "A voice is heard.",
 "main": "app.js",
 "scripts": {
   "test": "TODO you should perhaps create some tests here..."
 },
 "keywords": [],
 "author": "Me",
 "license": "MIT",
 "bin": {
   "helowrld": "./app.js"
 }
}
```

We're doing the bare minimum above, and for a real app you probably should create a set of tests to verify behavior. Most of the above should be pretty self-explanatory and easy to drop in and modify for your needs. The section

```
 "bin": {
   "helowrld": "./app.js"
 }
```

is worth noting, it just maps a command name to your app's source code.

Now that we have the packaging in place, it's time to create a Dockerized package. Make a `Dockerfile` in the same folder that looks like:

```
FROM node
RUN mkdir /app
WORKDIR /app

RUN npm install figlet

ADD ./app.js app.js
ADD ./package.json package.json
RUN npm install -g .
```

Effectively the above does the following:

1. Pulls the official `node` Dockerfile to base ours on,
2. Creates a working directory in the image,
3. Installs our dependency (`figlet`),
4. Copies in our app source and installs it as the command `helowrld`.

Now, we can build

```
docker build . -t my-helowrld-app
```

and run the image:
 
```
docker run my-helowrld-app helowrld

  _          _                    _     _
 | |__   ___| | _____      ___ __| | __| |
 | '_ \ / _ \ |/ _ \ \ /\ / / '__| |/ _` |
 | | | |  __/ | (_) \ V  V /| |  | | (_| |
 |_| |_|\___|_|\___/ \_/\_/ |_|  |_|\__,_|
```

There you have it. A single dependency application you can easily distribute.