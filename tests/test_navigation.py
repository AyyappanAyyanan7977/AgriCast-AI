import pytest
from agricast.services.navigation import PAGE_OPTIONS, resolve_navigation_target

@pytest.mark.parametrize('label,expected', [
    ('Climate & weather', 'Climate analysis'),
    ('Yield forecast', 'Yield forecasting'),
    ('Agronomy library', 'Agronomy guidance'),
    ('Farm data', 'Farm data'),
    ('Knowledge assistant', 'Knowledge assistant'),
    ('Tool integrations', 'Integrations'),
])
def test_legacy_navigation_labels_resolve(label, expected):
    result = resolve_navigation_target(label)
    assert result == expected
    assert result in PAGE_OPTIONS

def test_unknown_navigation_label_is_safe():
    assert resolve_navigation_target('made up destination') is None
