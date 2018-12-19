from conans import ConanFile, CMake, tools, Meson
from conanos.build import config_scheme
import os, shutil

class GdkpixbufConan(ConanFile):
    name = "gdk-pixbuf"
    version = "2.38.0"
    description = "An image loading library"
    url = "https://github.com/conanos/gdk-pixbuf"
    homepage = "https://github.com/GNOME/gdk-pixbuf"
    license = "LGPL-2+"
    patches = ["0001-add-options-for-loaders-cache-adn-tests-thumbnailer.patch"]
    exports = ["COPYING","io-png.c","io-tiff.c","gdk-pixbuf-io.c"] + patches
    generators = "visual_studio", "gcc"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = { 'shared': True, 'fPIC': True }

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx

        config_scheme(self)

    def requirements(self):
        self.requires.add("libtiff/4.0.10@conanos/stable")
        self.requires.add("glib/2.58.1@conanos/stable")
        self.requires.add("libpng/1.6.34@conanos/stable")

    def build_requirements(self):
        self.build_requires("libffi/3.299999@conanos/stable")
        self.build_requires("zlib/1.2.11@conanos/stable")

    def source(self):
        #tools.get("https://github.com/GNOME/gdk-pixbuf/archive/{version}.tar.gz".format(version=self.version))
        #extracted_dir = "{name}-{version}".format(name=self.name, version=self.version)
        #os.rename(extracted_dir, self._source_subfolder)
        #if self.settings.os == 'Windows':
        #    for src_file in ["io-tiff.c","gdk-pixbuf-io.c","io-png.c"]:
        #        shutil.copy2(os.path.join(self.source_folder,src_file), os.path.join(self.source_folder,self._source_subfolder,"gdk-pixbuf",src_file))
        url_ = "https://github.com/GNOME/gdk-pixbuf.git"
        branch_ = "master"
        git = tools.Git(folder=self.name)
        git.clone(url_, branch=branch_)
        with tools.chdir(self.name):
            for p in self.patches:
                self.run('git am %s'%(os.path.join('..',p)))
        os.rename(self.name, self._source_subfolder)
        if self.settings.os == 'Windows':
            for src_file in ["io-png.c","io-tiff.c","gdk-pixbuf-io.c"]:
                shutil.copy2(os.path.join(self.source_folder,src_file), os.path.join(self.source_folder,self._source_subfolder,"gdk-pixbuf",src_file))


    def build(self):
        pkg_config_paths=[ os.path.join(self.deps_cpp_info[i].rootpath, "lib", "pkgconfig") for i in ["libtiff","glib","libffi","zlib","libpng"] ]
        prefix = os.path.join(self.build_folder, self._build_subfolder, "install")
        defs = {'prefix' : prefix, "gir" : "false","x11": "false","man":"false","builtin_loaders":"all", "installed_tests":"false"}
        if self.settings.os == "Linux":
            defs.update({'libdir':'lib'})
        if self.settings.os == 'Windows':
            defs.update({'build_loaders_cache':'false', 'build_tests_and_thumbnailer':'false'})
        binpath=[ os.path.join(self.deps_cpp_info[i].rootpath, "bin") for i in ["glib","libffi"] ]
        meson = Meson(self)
        with tools.environment_append({
            'PATH' : os.pathsep.join(binpath + [os.getenv('PATH')]),
            }):
            meson.configure(defs=defs,source_dir=self._source_subfolder, build_dir=self._build_subfolder,pkg_config_paths=pkg_config_paths)
            meson.build()
            self.run('ninja -C {0} install'.format(meson.build_dir))

    def package(self):
        self.copy("*", dst=self.package_folder, src=os.path.join(self.build_folder,self._build_subfolder, "install"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)