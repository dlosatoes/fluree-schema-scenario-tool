"""Functionality of the fsst tool"""
from fsst.env_utils import runs_in_docker
from fsst.subcommand_deploy import deploy_main
from fsst.subcommand_guestdeploy import guestdeploy_main
from fsst.subcommand_dockerparams import dockerparams_main
from fsst.subcommand_artifactdeploy import artifactdeploy_main
from fsst.subcommand_test import test_main
from fsst.subcommand_artifact import artifact_main
from fsst.subcommand_guesttest import guesttest_main
from fsst.subcommand_dockerdeploy import dockerdeploy_main
from fsst.subcommand_dockertest import dockertest_main
from fsst.subcommand_versioncheck import versioncheck_main
from fsst.subcommand_dockerstart import dockerstart_main
from fsst.subcommand_dockerstop import dockerstop_main
from fsst.env_utils import get_createkey_and_port
from fsst.subcommand_freezepart import freezepart_main
from fsst.subcommand_checkpart import checkpart_main
from fsst.subcommand_unfreezedeps import unfreezedeps_main
from fsst.subcommand_refreezedeps import refreezedeps_main
from fsst.subcommand_freezetarget import freezetarget_main
from fsst.subcommand_artifactupgrade import artifactupgrade_main

VERSION = "0.3.0"
