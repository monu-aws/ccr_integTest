# Copyright OpenSearch Contributors
# SPDX-License-Identifier: Apache-2.0
#
# The OpenSearch Contributors require contributions made to
# this file be licensed under the Apache-2.0 license or a
# compatible open source license.

import os
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, List

from manifests.bundle_manifest import BundleManifest
from test_workflow.dependency_installer import DependencyInstaller
from test_workflow.integ_test.local_test_cluster import LocalTestCluster
from test_workflow.test_recorder.test_recorder import TestRecorder


class Topology:

    @classmethod
    @contextmanager
    def create(
            cls,
            number_of_cluster: int,
            dependency_installer: DependencyInstaller,
            work_dir: Path,
            component_name: str,
            additional_cluster_config: dict,
            bundle_manifest: BundleManifest,
            security_enabled: bool,
            component_test_config: str,
            test_recorder: TestRecorder) -> Generator[List, None, None]:
        clusters = []
        endpoints_list = []
        original_config = additional_cluster_config
        try:
            for i in range(number_of_cluster):
                cluster_port = 9200 + i
                original_config['cluster.name'] = "opensearch" + f'{i}'
                original_config['http.port'] = cluster_port
                clusters.append(
                    LocalTestCluster.create_cluster(
                        dependency_installer,
                        os.path.join(work_dir, f'{i}'),
                        component_name,
                        original_config,
                        bundle_manifest,
                        security_enabled,
                        component_test_config,
                        test_recorder,
                        cluster_port)
                )
            for i in range(number_of_cluster):
                endpoints_list.append({"endpoint": clusters[i].endpoint, "port": clusters[i].port, "transport": 9300 + i})
            yield endpoints_list
        finally:
            for cluster in clusters:
                cluster.terminate()
