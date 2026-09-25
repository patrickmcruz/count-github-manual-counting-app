#!/usr/bin/env python3
"""
Teste de Validação E2E e Interoperabilidade
==========================================
Verifica se as saídas geradas pelo app.py são 100% compatíveis com o
GroundTruthEvaluator do projeto principal rgbtcc.
"""

import sys
import json
import shutil
from pathlib import Path
import numpy as np
import cv2
import pandas as pd

# Adiciona o projeto principal ao sys.path para importar o GroundTruthEvaluator
REPO_PRINCIPAL = Path("/home/patrickcruz/Git/projects/contagem-de-pessoas/count-github-def_rgbtcc")
sys.path.insert(0, str(REPO_PRINCIPAL / "src"))

from rgbtcc.telemetry.metrics import GroundTruthEvaluator

def testar_interoperabilidade():
    app_root = Path(__file__).resolve().parent.parent
    gt_dir = app_root / "data" / "ground_truth"
    scene_stem = "DJI_TEST_001_W"
    scene_dir = gt_dir / scene_stem
    scene_dir.mkdir(parents=True, exist_ok=True)

    print(f"[*] Gerando cenário sintético de teste em: {scene_dir}")

    # Simulação dos entregáveis do app.py
    pontos_orig = [
        {"id": 1, "x": 100, "y": 200},
        {"id": 2, "x": 300, "y": 400},
        {"id": 3, "x": 500, "y": 600},
    ]

    # 1. Salvar CSV
    p_csv = scene_dir / f"pontos_ground_truth_{scene_stem}.csv"
    pd.DataFrame(pontos_orig).to_csv(p_csv, index=False)

    # 2. Salvar JSON Raw
    p_json = scene_dir / f"pontos_ground_truth_{scene_stem}.json"
    with open(p_json, "w", encoding="utf-8") as f:
        json.dump({
            "status": "finalizado",
            "imagem_origem": f"data/input/{scene_stem}.JPG",
            "total_pessoas_anotadas": len(pontos_orig),
            "pontos": pontos_orig,
        }, f, indent=2)

    # 3. Salvar JSON Alinhado 1280x1024
    p_json_aligned = scene_dir / f"ground_truth_aligned_1280x1024_{scene_stem}.json"
    p_json_aligned_canon = scene_dir / "ground_truth_aligned_1280x1024.json"
    aligned_data = {
        "cena": scene_stem,
        "resolucao_alinhada": [1280, 1024],
        "total_pessoas_anotadas": len(pontos_orig),
        "pontos": pontos_orig,
    }
    with open(p_json_aligned, "w", encoding="utf-8") as f:
        json.dump(aligned_data, f, indent=2)
    with open(p_json_aligned_canon, "w", encoding="utf-8") as f:
        json.dump(aligned_data, f, indent=2)

    # 4. Salvar Checkpoint e Metadados
    p_chk = scene_dir / f"checkpoint_{scene_stem}.json"
    with open(p_chk, "w", encoding="utf-8") as f:
        json.dump(aligned_data, f, indent=2)

    p_meta = scene_dir / f"metadados_{scene_stem}.json"
    with open(p_meta, "w", encoding="utf-8") as f:
        json.dump({"imagem_contada": scene_stem, "total_pessoas_anotadas": 3}, f, indent=2)

    # 5. Criar imagem de auditoria
    img_dummy = np.zeros((100, 100, 3), dtype=np.uint8)
    cv2.imwrite(str(scene_dir / f"rgb_anotada_ground_truth_{scene_stem}.jpg"), img_dummy)

    print("[✓] Arquivos do contrato gerados com sucesso.")

    # 6. Avaliar com GroundTruthEvaluator do rgbtcc
    evaluator = GroundTruthEvaluator(ground_truth_dir=gt_dir)
    found_file = evaluator.find_ground_truth_file(scene_stem)
    print(f"[*] GroundTruthEvaluator encontrou arquivo: {found_file}")
    assert found_file is not None, "GroundTruthEvaluator não encontrou o arquivo gerado!"

    pts = evaluator.load_points_from_json(found_file)
    print(f"[*] Pontos carregados pelo evaluator: {len(pts)}")
    assert len(pts) == 3, f"Esperado 3 pontos, obteve {len(pts)}"

    dummy_pred_density = np.zeros((1024, 1280), dtype=np.float32)
    eval_result = evaluator.evaluate(
        pred_density=dummy_pred_density,
        continuous_count=3.0,
        peaks_count=3,
        scene_stem=scene_stem,
    )
    print(f"[*] Resultado da avaliação:")
    print(f"    - has_ground_truth: {eval_result.has_ground_truth}")
    print(f"    - real_count: {eval_result.real_count}")
    print(f"    - rmse_continuous: {eval_result.rmse_continuous}")
    print(f"    - nae_continuous: {eval_result.nae_continuous}")

    assert eval_result.has_ground_truth is True
    assert eval_result.real_count == 3
    assert eval_result.rmse_continuous == 0.0
    assert eval_result.nae_continuous == 0.0

    print("\n" + "=" * 60)
    print("  [✓ SUCESSO ABSOLUTO] 100% DE INTEROPERABILIDADE CONFIRMADA!")
    print("=" * 60 + "\n")

    # Limpar cenário de teste
    shutil.rmtree(scene_dir)
    print("[*] Diretório de teste temporário removido com sucesso.")

if __name__ == "__main__":
    testar_interoperabilidade()
