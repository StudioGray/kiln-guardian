def test_import():
    import kiln_guardian
    assert hasattr(kiln_guardian, "__all__")
