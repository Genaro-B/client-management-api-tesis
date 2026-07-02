# Known Issues

## CI: pytest exit code 4 en Ubuntu

- **Síntoma**: Los tests pasan localmente (Windows, Python 3.14, pytest 9.0.3) pero fallan en GitHub Actions con exit code 4 de pytest.
- **Causa**: Error interno de pytest durante la colección de tests en `backend/tests/`, específico del runner de Ubuntu.
- **Tracking**: Pendiente de resolución. Ver investigación en `openspec/` o preguntar al agente.
- **Workaround**: `python -m unittest discover` funciona, pero los tests usan fixtures de pytest.

## Streamlit: comando no reconocido en Windows

- **Síntoma**: `streamlit run app.py` → error "no se reconoce como programa"
- **Causa**: El ejecutable de Streamlit no está en el PATH de Windows
- **Solución**: Usar `python -m streamlit run app.py` en lugar de `streamlit run app.py`
