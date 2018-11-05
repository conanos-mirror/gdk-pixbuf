from conans import ConanFile, CMake, tools, AutoToolsBuildEnvironment
import os
import shutil

class GdkpixbufConan(ConanFile):
    name = "gdk-pixbuf"
    version = "2.36.2"
    description = "An image loading library"
    url = "https://github.com/conanos/gdk-pixbuf"
    homepage = "https://github.com/GNOME/gdk-pixbuf"
    license = "LGPLv2Plus"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=True"
    generators = "cmake"
    requires = ('libjpeg-turbo/1.5.2@conanos/dev','glib/2.58.0@conanos/dev','libpng/1.6.34@conanos/dev',
                'libtiff/4.0.9@conanos/dev','zlib/1.2.11@conanos/dev',

                'gtk-doc-lite/1.27@conanos/dev',
                'libffi/3.3-rc0@conanos/dev',
                'gobject-introspection/1.58.0@conanos/dev'
                )

    source_subfolder = "source_subfolder"

    def source(self):
        tools.get("https://github.com/GNOME/gdk-pixbuf/archive/{version}.tar.gz".format(version=self.version))
        extracted_dir = "{name}-{version}".format(name=self.name, version=self.version)
        os.rename(extracted_dir, self.source_subfolder)

    def build(self):
        with tools.chdir(self.source_subfolder):
            with tools.environment_append({
                'PKG_CONFIG_PATH':'%s/lib/pkgconfig:%s/lib/pkgconfig:%s/lib/pkgconfig:%s/lib/pkgconfig:%s/lib/pkgconfig:%s/lib/pkgconfig:%s/lib/pkgconfig'
                %(self.deps_cpp_info["libjpeg-turbo"].rootpath, self.deps_cpp_info["glib"].rootpath,
                self.deps_cpp_info["libpng"].rootpath, self.deps_cpp_info["libtiff"].rootpath,
                self.deps_cpp_info["zlib"].rootpath, self.deps_cpp_info["libffi"].rootpath,
                self.deps_cpp_info["gobject-introspection"].rootpath,),
                'LD_LIBRARY_PATH' : "%s/lib:%s/lib"%(self.deps_cpp_info["libffi"].rootpath, self.deps_cpp_info["glib"].rootpath,),
                'LIBRARY_PATH' : "%s/lib:%s/lib"%(self.deps_cpp_info["libtiff"].rootpath, self.deps_cpp_info["libjpeg-turbo"].rootpath),
                'C_INCLUDE_PATH': "%s/include:%s/include"%(self.deps_cpp_info["libtiff"].rootpath, self.deps_cpp_info["libjpeg-turbo"].rootpath),
                }):

                shutil.copy('%s/share/gtk-doc/data/gtk-doc.make'%(self.deps_cpp_info["gtk-doc-lite"].rootpath), '.')
                self.run("autoreconf -f -i")

                _args = ["--prefix=%s/builddir"%(os.getcwd()), '--libdir=%s/builddir/lib'%(os.getcwd()) ,
                         "--with-included-loaders", "--enable-gio-sniffing=no", "--enable-introspection"]
                if self.options.shared:
                    _args.extend(['--enable-shared=yes','--enable-static=no'])
                else:
                    _args.extend(['--enable-shared=no','--enable-static=yes'])
                self.run('./configure %s'%(' '.join(_args)))#space
                
                self.run('make -j4')
                self.run('make install')


    def package(self):
        if tools.os_info.is_linux:
            with tools.chdir(self.source_subfolder):
                self.copy("*", src="%s/builddir"%(os.getcwd()))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)