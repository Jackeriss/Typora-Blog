## 使用 py2exe 打包 Python 程序

2014-04-11 17:44:00

py2exe 可以将一个 Python 程序打包成 Windows 下的 exe 可执行文件。使用 py2exe 打包需要编写一个打包脚本，执行后可以得到打包文件。对于 32 位版本，py2exe 可以将程序打包成单文件；对于 64 位版本，暂时还不支持打包成单文件。不过，无论如何压缩，目前 py2exe 打包出来的程序都还是偏大的。

#### 参数详解

```python
from distutils.core import setup
import py2exe

includes = ["encodings", "encodings.*", "sip"]

options = {"py2exe":
    {"compressed": 1,
     "optimize": 2,
     "ascii": 1,
     "includes": includes,
     "bundle_files": 1
     }
    }
setup(options=options,
      zipfile=None,
      windows=[{"script": "example.py",
                "icon_resources": [(1, "icon.ico")]
               }],
      #data_files=[("*",["#","#","#"]),]
     )
```

选项中`ncludes`是需要包含的文件，这里的`sip`是 PyQt 程序打包时需要添加的，如果不是 PyQt 程序不需要此项。

`dll_excludes`是需要排除的 dll 文件，如果什么都不写，有可能会报`error: MSVCP90.dll: No such file or directory`错误。你可以在微软官网下载一个`MSVCP90.dll`并将其放入系统路径内。

`compressed`为 1，则压缩文件。

`ptimize`为优化级别，默认为 0。

`ascii`指**不**自动包含 encodings 和 codecs。

`bundle_files`是指将程序打包成单文件（此时除了 exe 文件外，还会生成一个 zip 文件。如果不需要 zip 文件，还需要设置`zipfile = None`）。1表示 pyd 和 dll 文件会被打包到单文件中，且不能从文件系统中加载 Python 模块；值为2表示 pyd 和 dll 文件会被打包到单文件中，但是可以从文件系统中加载 Python 模块。**64 位的 py2exe 不要添加本句**。

```python
windows=[{"script": "example.py",
          "icon_resources": [(1, "icon.ico")]
         }]
```

这里使用的是`windows`，即没有命令行窗口出现，如果使用`console`则表示有命令行窗口出现。

`script`是你要打包的程序的执行入口文件。

`icon_resources`可以设置打包生成的 exe 文件的图标。

`data_files`中可以添加一起打包的文件，在`*`处写文件夹路径，在`#`处写要一起打包的文件名。

执行该文件，会得到一个 build 文件夹和一个 dist 文件夹。其中，dist 文件夹，就是你得到的打包程序。

如果按照上述代码执行成功，则应该 dist 文件夹中，只包括程序的 exe 文件和w9xpopen.exe。w9xpopen.exe 是针对 windows 9x 版本的，一般来说该文件并不需要。

如果`bundle_files`不为 1、2，则 dist 文件夹中还会包括一些 dll 文件和 pyd 文件。如果`bundle_files`为 2，dist 文件夹会包括一个 python##.dll 文件，如果为 1 则不会。

如果没有使用`zipfile=None`，还会生成一个 library.zip 文件。

#### 常见问题

Windows Vista 以上版本的系统下图标显示异常

按照上面的代码打包来的 exe 程序，在 windows XP 系统下，我们可以看到 exe 的图标。但是当把程序拷贝到 vista/win7 下时，exe 图标确变成了默认的”窗口“图标，无论怎么变换试图模式都使如此。

首先先介绍一下 ico 文件，这对于理解其解决方案有很大帮助。

ico 文件是 Windows 下图片格式，我们看到的文件夹，执行文件等都有不同的图标显示，并且当我们切换视图模式时，文件的图标会以”不同“尺寸显示，确切的说，应该是不同的图标文件（尺寸亦不同）。ico 文件里面可以有多个不同的图标文件以适应不同的视图模式，并且这些图标文件通常按尺寸大小的顺序存放。以 Windows XP 下支持的 ico 尺寸为 16 x 16，32 x 32 和 48 x 48。Vista 以上的系统下则最多可以支持 256 x 256。

问题关键在于 ico 文件中图标的顺序问题，XP 对顺序要求不高，无论是图标是按尺寸的正序还是倒序都可以正常显示，而然在 Vista 以上的系统下确只能倒序。

推荐几个 ico 编辑工具来解决这个问题，首先是 Greenfish Icon Editor Pro，该工具不仅可以编辑图标文件，而且可以修改图标文件的顺序。然后 IcoFX 也有类似的功能。最后就是 Icon Manager，这个小工具专门用来修改 ico 文件的图片顺序。