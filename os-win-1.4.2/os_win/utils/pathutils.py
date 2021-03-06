# Copyright 2013 Cloudbase Solutions Srl
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import contextlib
import ctypes
import os
import shutil
import sys
import tempfile

from oslo_log import log as logging
from oslo_utils import fileutils
import six

from os_win._i18n import _
from os_win import _utils
from os_win import exceptions
from os_win.utils import _acl_utils
from os_win.utils import win32utils

if sys.platform == 'win32':
    from ctypes import wintypes
    kernel32 = ctypes.windll.kernel32

LOG = logging.getLogger(__name__)

ERROR_DIR_IS_NOT_EMPTY = 145


class PathUtils(object):
    _FILE_ATTRIBUTE_REPARSE_POINT = 0x0400

    def __init__(self):
        self._win32_utils = win32utils.Win32Utils()
        self._acl_utils = _acl_utils.ACLUtils()

    def open(self, path, mode):
        """Wrapper on __builtin__.open used to simplify unit testing."""
        from six.moves import builtins
        return builtins.open(path, mode)

    def exists(self, path):
        return os.path.exists(path)

    def makedirs(self, path):
        os.makedirs(path)

    def remove(self, path):
        os.remove(path)

    def rename(self, src, dest):
        os.rename(src, dest)

    def copy_dir(self, src, dest):
        shutil.copytree(src, dest)

    def copyfile(self, src, dest):
        self.copy(src, dest)

    def copy(self, src, dest, fail_if_exists=True):
        """Copies a file to a specified location.

        :param fail_if_exists: if set to True, the method fails if the
                               destination path exists.
        """
        # With large files this is 2x-3x faster than shutil.copy(src, dest),
        # especially when copying to a UNC target.
        if os.path.isdir(dest):
            src_fname = os.path.basename(src)
            dest = os.path.join(dest, src_fname)

        try:
            self._win32_utils.run_and_check_output(
                kernel32.CopyFileW,
                ctypes.c_wchar_p(src),
                ctypes.c_wchar_p(dest),
                wintypes.BOOL(fail_if_exists),
                kernel32_lib_func=True)
        except exceptions.Win32Exception as exc:
            err_msg = _('The file copy from %(src)s to %(dest)s failed.'
                        'Exception: %(exc)s')
            raise IOError(err_msg % dict(src=src, dest=dest, exc=exc))

    def move_folder_files(self, src_dir, dest_dir):
        """Moves the files of the given src_dir to dest_dir.

        It will ignore any nested folders.

        :param src_dir: Given folder from which to move files.
        :param dest_dir: Folder to which to move files.
        """

        for fname in os.listdir(src_dir):
            src = os.path.join(src_dir, fname)
            # ignore subdirs.
            if os.path.isfile(src):
                self.rename(src, os.path.join(dest_dir, fname))

    @_utils.retry_decorator(exceptions=exceptions.OSWinException,
                            error_codes=[ERROR_DIR_IS_NOT_EMPTY])
    def rmtree(self, path):
        try:
            shutil.rmtree(path)
        except exceptions.WindowsError as ex:
            # NOTE(claudiub): convert it to an OSWinException in order to use
            # the retry_decorator.
            raise exceptions.OSWinException(six.text_type(ex),
                                            error_code=ex.winerror)

    def check_create_dir(self, path):
        if not self.exists(path):
            LOG.debug('Creating directory: %s', path)
            self.makedirs(path)

    def check_remove_dir(self, path):
        if self.exists(path):
            LOG.debug('Removing directory: %s', path)
            self.rmtree(path)

    def is_symlink(self, path):
        if sys.version_info >= (3, 2):
            return os.path.islink(path)

        file_attr = self._win32_utils.run_and_check_output(
            kernel32.GetFileAttributesW,
            six.text_type(path),
            kernel32_lib_func=True)

        return bool(os.path.isdir(path) and (
            file_attr & self._FILE_ATTRIBUTE_REPARSE_POINT))

    def create_sym_link(self, link, target, target_is_dir=True):
        """If target_is_dir is True, a junction will be created.

        NOTE: Juctions only work on same filesystem.
        """

        create_symlink = kernel32.CreateSymbolicLinkW
        create_symlink.argtypes = (
            ctypes.c_wchar_p,
            ctypes.c_wchar_p,
            ctypes.c_ulong,
        )
        create_symlink.restype = ctypes.c_ubyte

        self._win32_utils.run_and_check_output(create_symlink,
                                               link,
                                               target,
                                               target_is_dir,
                                               kernel32_lib_func=True)

    def create_temporary_file(self, suffix=None, *args, **kwargs):
        fd, tmp_file_path = tempfile.mkstemp(suffix=suffix, *args, **kwargs)
        os.close(fd)
        return tmp_file_path

    @contextlib.contextmanager
    def temporary_file(self, suffix=None, *args, **kwargs):
        """Creates a random, temporary, closed file, returning the file's

        path. It's different from tempfile.NamedTemporaryFile which returns
        an open file descriptor.
        """

        tmp_file_path = None
        try:
            tmp_file_path = self.create_temporary_file(suffix, *args, **kwargs)
            yield tmp_file_path
        finally:
            if tmp_file_path:
                fileutils.delete_if_exists(tmp_file_path)

    def add_acl_rule(self, path, trustee_name,
                     access_rights, access_mode,
                     inheritance_flags=0):
        """Adds the requested access rule to a file or object.

        Can be used for granting/revoking access.
        """
        p_to_free = []

        try:
            sec_info = self._acl_utils.get_named_security_info(
                obj_name=path,
                obj_type=_acl_utils.SE_FILE_OBJECT,
                security_info_flags=_acl_utils.DACL_SECURITY_INFORMATION)
            p_to_free.append(sec_info['pp_sec_desc'].contents)

            access = _acl_utils.EXPLICIT_ACCESS()
            access.grfAccessPermissions = access_rights
            access.grfAccessMode = access_mode
            access.grfInheritance = inheritance_flags
            access.Trustee.TrusteeForm = _acl_utils.TRUSTEE_IS_NAME
            access.Trustee.pstrName = ctypes.c_wchar_p(trustee_name)

            pp_new_dacl = self._acl_utils.set_entries_in_acl(
                entry_count=1,
                p_explicit_entry_list=ctypes.pointer(access),
                p_old_acl=sec_info['pp_dacl'].contents)
            p_to_free.append(pp_new_dacl.contents)

            self._acl_utils.set_named_security_info(
                obj_name=path,
                obj_type=_acl_utils.SE_FILE_OBJECT,
                security_info_flags=_acl_utils.DACL_SECURITY_INFORMATION,
                p_dacl=pp_new_dacl.contents)
        finally:
            for p in p_to_free:
                self._win32_utils.local_free(p)

    def copy_acls(self, source_path, dest_path):
        p_to_free = []

        try:
            sec_info_flags = _acl_utils.DACL_SECURITY_INFORMATION
            sec_info = self._acl_utils.get_named_security_info(
                obj_name=source_path,
                obj_type=_acl_utils.SE_FILE_OBJECT,
                security_info_flags=sec_info_flags)
            p_to_free.append(sec_info['pp_sec_desc'].contents)

            self._acl_utils.set_named_security_info(
                obj_name=dest_path,
                obj_type=_acl_utils.SE_FILE_OBJECT,
                security_info_flags=sec_info_flags,
                p_dacl=sec_info['pp_dacl'].contents)
        finally:
            for p in p_to_free:
                self._win32_utils.local_free(p)
