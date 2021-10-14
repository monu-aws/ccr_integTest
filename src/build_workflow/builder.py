# SPDX-License-Identifier: Apache-2.0
#
# The OpenSearch Contributors require contributions made to
# this file be licensed under the Apache-2.0 license or a
# compatible open source license.

import os

from paths.script_finder import ScriptFinder

"""
This class is responsible for executing the build for a component and passing the results to a build recorder.
It will notify the build recorder of build information such as repository and git ref, and any artifacts generated by the build.
Artifacts found in "<build root>/artifacts/<maven|plugins|libs|dist|core-plugins>" will be recognized and recorded.
"""


class Builder:
    def __init__(self, component_name, git_repo, build_recorder):
        """
        Construct a new Builder instance.
        :param component_name: The name of the component to build.
        :param git_repo: A GitRepository instance containing the checked-out code.
        :param build_recorder: The build recorder that will capture build information and artifacts.
        """

        self.component_name = component_name
        self.git_repo = git_repo
        self.build_recorder = build_recorder
        self.output_path = "artifacts"
        self.artifacts_path = os.path.join(
            self.git_repo.working_directory, self.output_path
        )

    def build(self, target):
        build_script = ScriptFinder.find_build_script(
            target.name, self.component_name, self.git_repo.working_directory
        )
        build_command = " ".join(
            [
                build_script,
                "-v",
                target.version,
                "-p",
                target.platform,
                "-a",
                target.arch,
                "-s",
                str(target.snapshot).lower(),
                "-o",
                self.output_path,
            ]
        )
        self.git_repo.execute(build_command)
        self.build_recorder.record_component(self.component_name, self.git_repo)

    def export_artifacts(self):
        for artifact_type in ["maven", "dist", "plugins", "libs", "core-plugins"]:
            for dir, dirs, files in os.walk(
                os.path.join(self.artifacts_path, artifact_type)
            ):
                for file_name in files:
                    absolute_path = os.path.join(dir, file_name)
                    relative_path = os.path.relpath(absolute_path, self.artifacts_path)
                    self.build_recorder.record_artifact(
                        self.component_name, artifact_type, relative_path, absolute_path
                    )
