"""Testing contacts, not finished!"""

import pytest

import grid3d_maps.contact.grid3d_contact_map as grid3d_contacts

# =============================================================================
# Do tests
# =============================================================================


@pytest.mark.skip("Take this later")
def test_contact1a(datatree):
    """Test HC contacts with YAML config example 1a"""
    result = datatree / "contacts1a_folder"
    result.mkdir(parents=True)
    grid3d_contacts.main(["--config", "tests/yaml/contact1a.yml"])
