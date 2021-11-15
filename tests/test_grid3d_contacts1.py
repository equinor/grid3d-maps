"""Testing contacts, not finished!"""
import xtgeoapp_grd3dmaps.contact.grid3d_contact_map as grid3d_contacts

# =============================================================================
# Do tests
# =============================================================================


def test_contact1a(datatree):
    """Test HC contacts with YAML config example 1a"""
    result = datatree / "contacts1a_folder"
    result.mkdir(parents=True)
    grid3d_contacts.main(["--config", "tests/yaml/contact1a.yml"])
