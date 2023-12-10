/*
 * Ceph - scalable distributed file system
 *
 * Copyright (C) 2011 Stanislav Sedov <stas@FreeBSD.org>
 *
 * This is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License version 2.1, as published by the Free Software
 * Foundation.  See file COPYING.
 */

#include <sys/types.h>
#include <sys/xattr.h>

#include "common/xattr.h"

/*
 * Sets extended attribute on a file.
 * Returns 0 on success, -1 on failure.
 */
int
ceph_os_setxattr(const char *path, const char *name,
    const void *value, size_t size)
{
	int error = -1;

	error = setxattr(path, name, value, size, 0);

	return (error);
}

int
ceph_os_fsetxattr(int fd, const char *name, const void *value,
    size_t size)
{
	int error = -1;
	error = fsetxattr(fd, name, value, size, 0);

	return (error);
}

ssize_t
ceph_os_getxattr(const char *path, const char *name,
void *value, size_t size)
{
	ssize_t error = -1;
	error = getxattr(path, name, value, size);

	return (error);
}

ssize_t
ceph_os_fgetxattr(int fd, const char *name, void *value,
    size_t size)
{
	ssize_t error = -1;
	error = fgetxattr(fd, name, value, size);

	return (error);
}

ssize_t
ceph_os_listxattr(const char *path, char *list, size_t size)
{
	ssize_t error = -1;
	error = listxattr(path, list, size);

	return (error);
}

ssize_t
ceph_os_flistxattr(int fd, char *list, size_t size)
{
	ssize_t error = -1;
	error = flistxattr(fd, list, size);

	return (error);
}

int
ceph_os_removexattr(const char *path, const char *name)
{
	int error = -1;
	error = removexattr(path, name);
	return (error);
}

int
ceph_os_fremovexattr(int fd, const char *name)
{
	int error = -1;
	error = fremovexattr(fd, name);

	return (error);
}
