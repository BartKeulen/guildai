# Copyright 2017 TensorHub, Inc.
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

import click

from guild import click_util
from . import runs_support

def label_params(fn):
    runs_support.runs_arg(fn)
    click_util.append_params(fn, [
        click.Argument(("label",), required=False),
    ])
    runs_support.op_and_label_filters(fn)
    runs_support.status_filters(fn)
    runs_support.scope_options(fn)
    click_util.append_params(fn, [
        click.Option(
            ("--clear",),
            help="Clear the run's label.",
            is_flag=True),
        click.Option(
            ("-y", "--yes",),
            help="Do not prompt before modifying labels.",
            is_flag=True),
    ])
    return fn

@click.command()
@label_params

@click.pass_context
@click_util.use_args
@click_util.render_doc

def label(ctx, args):
    """Set run labels.

    If `LABEL` is provided, the command will label the selected runs.

    Select runs to label using one or more `RUN` arguments. See SELECT
    RUNS below for information on selecting runs.

    If `RUN` isn't specified, the most recent run is selected.

    To clear a run label, use the ``--clear`` option.

    By default Guild will prompt you before making any changes. If you
    want to apply the changes without being prompted, use the
    ``--yes`` option.

    {{ runs_support.runs_arg }}

    If a `RUN` argument is not specified, ``0`` is assumed (the most
    recent run).

    {{ runs_support.op_and_label_filters }} {{
    runs_support.status_filters }} {{ runs_support.scope_options }}

    """
    from . import runs_impl
    runs_impl.label(args, ctx)
