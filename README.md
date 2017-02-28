# Export Adobe Lightroom Faces

This script exports tagged faces from the Adobe Lightroom SQLlite Database. Just give the script a name you entered in Lightroom and you get JPGs just with the faces and not the whole image.

### 1. Install dependencies

There are a few library dependencies, which you can install using
[pip](https://pip.pypa.io/en/stable/quickstart/):

```shell
$ pip install -r requirements.txt
```

### 2. Usage



```shell
$ ./getfaces.py -d <path to Lightroom DB File> -o <output path> -n <Name of the person> [-ee extension1, extension2,...]
```

<h3>License</h3>
<strong>exportlightroomfaces</strong> is released under the [MIT License](https://github.com/ThomasMoritz/exportlightroomfaces/blob/master/LICENSE).
