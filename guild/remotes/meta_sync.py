# Copyright 2017-2020 TensorHub, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import absolute_import
from __future__ import division

import hashlib
import os
import re

from guild import click_util
from guild import remote as remotelib
from guild import var

from guild.commands import runs_impl


class MetaSyncRemote(remotelib.Remote):
    def __init__(self, runs_dir, deleted_runs_dir=None):
        self._runs_dir = runs_dir
        self._deleted_runs_dir = deleted_runs_dir

    def list_runs(self, verbose=False, deleted=False, **filters):
        if deleted and not self._deleted_runs_dir:
            raise remotelib.OperationNotSupported(
                "remote '%s' does not support '--delete' option" % self.name
            )
        self._sync_runs_meta()
        runs_dir = self._deleted_runs_dir if deleted else self._runs_dir
        if not os.path.exists(runs_dir):
            return
        assert not filters.get("archive"), filters
        assert not filters.get("remote"), filters
        args = click_util.Args(
            verbose=verbose,
            deleted=False,
            archive=runs_dir,
            remote=None,
            json=False,
            **filters
        )
        runs_impl.list_runs(args)

    def _sync_runs_meta(self, force=False):
        raise NotImplementedError()

    def filtered_runs(self, **filters):
        self._sync_runs_meta()
        args = click_util.Args(archive=self._runs_dir, remote=None, runs=[], **filters)
        return runs_impl.runs_for_args(args)

    def delete_runs(self, **opts):
        if not self._deleted_runs_dir and not opts.get("permanent"):
            raise remotelib.OperationNotSupported(
                "remote '%s' does not support non permanent deletes\n"
                "Use the '--permanent' with this command and try again." % self.name
            )
        args = click_util.Args(archive=self._runs_dir, remote=None, **opts)
        self._sync_runs_meta()
        if args.permanent:
            preview = (
                "WARNING: You are about to permanently delete "
                "the following runs on %s:" % self.name
            )
            confirm = "Permanently delete these runs?"
        else:
            preview = "You are about to delete the following runs on %s:" % self.name
            confirm = "Delete these runs?"
        no_runs_help = "Nothing to delete."

        def delete_f(selected):
            self._delete_runs(selected, args.permanent)
            self._new_meta_id()
            self._sync_runs_meta(force=True)

        try:
            runs_impl.runs_op(
                args,
                None,
                preview,
                confirm,
                no_runs_help,
                delete_f,
                confirm_default=not args.permanent,
            )
        except SystemExit as e:
            self._reraise_system_exit(e)

    def _delete_runs(self, runs, permanent):
        raise NotImplementedError()

    def _reraise_system_exit(self, e, deleted=False):
        if not e.args[0]:
            raise e
        exit_code = e.args[1]
        msg = e.args[0].replace(
            "guild runs list",
            "guild runs list %s-r %s" % (deleted and "-d " or "", self.name),
        )
        raise SystemExit(msg, exit_code)

    def restore_runs(self, **opts):
        if not self._deleted_runs_dir:
            raise remotelib.OperationNotSupported()
        self._sync_runs_meta()
        args = click_util.Args(archive=self._deleted_runs_dir, remote=None, **opts)
        preview = "You are about to restore the following runs on %s:" % self.name
        confirm = "Restore these runs?"
        no_runs_help = "Nothing to restore."

        def restore_f(selected):
            self._restore_runs(selected)
            self._sync_runs_meta(force=True)

        try:
            runs_impl.runs_op(
                args,
                None,
                preview,
                confirm,
                no_runs_help,
                restore_f,
                confirm_default=True,
            )
        except SystemExit as e:
            self._reraise_system_exit(e, deleted=True)

    def _restore_runs(self, runs):
        raise NotImplementedError()

    def purge_runs(self, **opts):
        if not self._deleted_runs_dir:
            raise remotelib.OperationNotSupported()
        self._sync_runs_meta()
        args = click_util.Args(archive=self._deleted_runs_dir, remote=None, **opts)
        preview = (
            "WARNING: You are about to permanently delete "
            "the following runs on %s:" % self.name
        )
        confirm = "Permanently delete these runs?"
        no_runs_help = "Nothing to purge."

        def purge_f(selected):
            self._purge_runs(selected)
            self._sync_runs_meta(force=True)

        try:
            runs_impl.runs_op(
                args,
                None,
                preview,
                confirm,
                no_runs_help,
                purge_f,
                confirm_default=False,
            )
        except SystemExit as e:
            self._reraise_system_exit(e, deleted=True)

    def _purge_runs(self, runs):
        raise NotImplementedError()

    def run_info(self, **opts):
        self._sync_runs_meta()
        args = click_util.Args(**opts)
        args.archive = self._runs_dir
        args.remote = None
        args.private_attrs = False
        runs_impl.run_info(args, None)


def local_meta_dir(remote_name, key):
    base_dir = var.remote_dir(_safe_filename(remote_name))
    key_hash = hashlib.md5(key.encode()).hexdigest()
    return os.path.join(base_dir, "meta", key_hash)


def _safe_filename(s):
    if not s:
        return s
    return re.sub(r"\W+", "-", s).strip("-") or "-"