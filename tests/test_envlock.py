from ecoscope_workflows.envlock import MicromambaEnvExport, mamba_env_export


def test_mamba_env_export():
    export = mamba_env_export()
    assert isinstance(export, MicromambaEnvExport)
