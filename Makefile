#
# **************************************************************                *
# *                                                            *
# * Author: sunbin (2023)                                      *
# * URL: https://github.com/samba-team/samba				   *
# *                                                            *
# * Copyright notice:                                          *
# * Free use of this C++ Makefile template is permitted under  *
# * the guidelines and in accordance with the the MIT License  *
# * http://www.opensource.org/licenses/MIT                     *
# *                                                            *
# **************************************************************
#

TOPDIR := $(shell /bin/pwd)
core_src_dir = $(TOPDIR)
build_dir = $(TOPDIR)/build
ceph_src_dir = $(core_src_dir)/nautilus
ceph_dest_dir = $(build_dir)/SOURCES/ceph-v14.2.22
boost_src_dir = $(TOPDIR)/boost
ceph = ceph-v14.2.22
all:  .build_ceph
  
.build_ceph:
	(if [ -d $(build_dir) ]; then rm -rf $(build_dir); fi)
	(mkdir -p $(build_dir))
	(mkdir -p $(build_dir)/{BUILD,BUILDROOT,RPMS,SOURCES,SPECS,SRPMS})
	(if [ -d $(ceph_dest_dir) ]; then mkdir -p $(ceph_dest_dir); fi)

	echo "---------- copy ceph files ----------"
	cp -a $(ceph_src_dir) $(ceph_dest_dir)
	cp -a $(boost_src_dir) $(ceph_dest_dir)/src
	(cd $(build_dir)/SOURCES; \
		rm -rf $(ceph)/.git; \
		tar zcvf $(ceph).tar.gz $(ceph); \
		rm -rf $(ceph))

	echo "---------- copy spec ----------"
	(cp -af $(core_src_dir)/ceph.spec $(build_dir)/SPECS/)

	echo "---------- build ceph ----------"
	(rpmbuild -ba --define="_topdir $(build_dir)" $(build_dir)/SPECS/ceph.spec)

install:
	@(cd $(build_dir)/RPMS/noarch; rpm -vih *.noarch.rpm --force)
	@(cd $(build_dir)/RPMS/x86_64; rpm -vih *.x86_64.rpm --force)
clean:
	-rm -rf $(build_dir)