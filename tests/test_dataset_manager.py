import pandas as pd
import pytest
from agricast.services.dataset_manager import save_uploaded_dataset, validate_uploaded_dataset


def test_upload_replaces_data_and_invalidates_stale_model_and_report(tmp_path):
    data = tmp_path / 'data' / 'farm.csv'
    target = tmp_path / 'data' / 'target.txt'
    model = tmp_path / 'models' / 'model.joblib'
    report = tmp_path / 'reports' / 'evaluation.json'
    provenance = tmp_path / 'data' / 'DATA_PROVENANCE.md'
    for p in (model, report, provenance):
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text('stale', encoding='utf-8')
    frame = pd.DataFrame({'rainfall_mm': range(25), 'temperature_c': range(25, 50), 'yield_tonnes_ha': [x/10 for x in range(25)]})
    saved = save_uploaded_dataset(frame, 'yield_tonnes_ha', data, target, model, report, provenance)
    assert len(pd.read_csv(data)) == 25
    assert target.read_text(encoding='utf-8') == 'yield_tonnes_ha'
    assert saved.shape == frame.shape
    assert not model.exists() and not report.exists() and not provenance.exists()


def test_upload_rejects_non_numeric_target_without_saving(tmp_path):
    frame = pd.DataFrame({'rain': range(20), 'yield': ['unknown'] * 20})
    with pytest.raises(ValueError, match='numeric values'):
        save_uploaded_dataset(frame, 'yield', tmp_path/'farm.csv', tmp_path/'target.txt')
    assert not (tmp_path/'farm.csv').exists()


def test_upload_deduplicates_headers_and_preserves_first_column():
    frame = pd.DataFrame([[1, 999, 2], [3, 888, 4]], columns=['rain', 'rain', 'yield'])
    result = validate_uploaded_dataset(frame, 'yield')
    assert result.columns.tolist() == ['rain', 'yield']
    assert result['rain'].tolist() == [1, 3]
