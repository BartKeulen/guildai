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

import errno
import logging
import os

from guild import cli
from guild import log

def main(args, ctx):
    log.init_logging(args.log_level or logging.INFO)
    if args.chdir and not os.path.exists(args.chdir):
        cli.error("%s does not exist" % e.filename)
    ctx.obj["cwd"] = args.chdir or "."
