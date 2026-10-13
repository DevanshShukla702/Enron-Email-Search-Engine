<#
.SYNOPSIS
    Task runner script for Enron Email IR Project (Windows PowerShell)

.DESCRIPTION
    Provides simple commands to download dataset, ingest, preprocess, build indexes,
    run evaluation, execute tests, launch backend and frontend.
#>

param (
    [Parameter(Position=0)]
    [string]$Command = "help",

    [Parameter(Position=1)]
    [string]$Arg1 = ""
)

$ErrorActionPreference = "Stop"
$ProjectRoot = $PSScriptRoot

function Show-Help {
    Write-Host "==========================================================" -ForegroundColor Cyan
    Write-Host " Enron Email IR System - PowerShell Task Runner" -ForegroundColor Cyan
    Write-Host "==========================================================" -ForegroundColor Cyan
    Write-Host "Usage: .\run.ps1 <command>"
    Write-Host ""
    Write-Host "Commands:"
    Write-Host "  download     Download the CMU Enron email corpus"
    Write-Host "  ingest       Ingest raw emails into SQLite database"
    Write-Host "  preprocess   Preprocess text and build thread relationships"
    Write-Host "  build-tfidf  Build the TF-IDF sparse matrix index"
    Write-Host "  build-bm25   Build the BM25 probabilistic index"
    Write-Host "  build-dense  Build the Sentence Transformer FAISS dense index"
    Write-Host "  build-all    Build all search indexes in sequence"
    Write-Host "  evaluate     Run the comprehensive evaluation benchmark"
    Write-Host "  test         Run pytest unit and integration tests"
    Write-Host "  backend      Start the FastAPI backend server (port 8000)"
    Write-Host "  frontend     Start the Vite React frontend (port 5173)"
    Write-Host "  health       Run system integrity and index health check"
    Write-Host "  clean        Clean temporary files and caches"
    Write-Host "=========================================================="
}

switch ($Command.ToLower()) {
    "download" {
        Write-Host "Downloading Enron dataset..." -ForegroundColor Green
        python scripts/download_dataset.py
    }
    "ingest" {
        Write-Host "Ingesting dataset into SQLite database..." -ForegroundColor Green
        python scripts/ingest_dataset.py
    }
    "preprocess" {
        Write-Host "Preprocessing emails and building threads..." -ForegroundColor Green
        python scripts/preprocess_dataset.py
        python scripts/build_threads.py
    }
    "build-tfidf" {
        Write-Host "Building TF-IDF index..." -ForegroundColor Green
        python scripts/build_tfidf_index.py
    }
    "build-bm25" {
        Write-Host "Building BM25 index..." -ForegroundColor Green
        python scripts/build_bm25_index.py
    }
    "build-dense" {
        Write-Host "Building Sentence Transformer dense index..." -ForegroundColor Green
        python scripts/build_dense_index.py
    }
    "build-all" {
        Write-Host "Building all indexes..." -ForegroundColor Green
        python scripts/build_all_indexes.py
    }
    "evaluate" {
        Write-Host "Running IR evaluation pipeline..." -ForegroundColor Green
        python scripts/run_evaluation.py
    }
    "test" {
        Write-Host "Running test suite..." -ForegroundColor Green
        pytest backend/tests -v
    }
    "backend" {
        Write-Host "Starting FastAPI backend server on http://127.0.0.1:8000 ..." -ForegroundColor Green
        python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
    }
    "frontend" {
        Write-Host "Starting Vite frontend dev server on http://localhost:5173 ..." -ForegroundColor Green
        Set-Location "$ProjectRoot/frontend"
        npm run dev
    }
    "health" {
        Write-Host "Running health check..." -ForegroundColor Green
        python scripts/health_check.py
    }
    "clean" {
        Write-Host "Cleaning caches and temporary files..." -ForegroundColor Yellow
        Get-ChildItem -Path . -Include __pycache__ -Recurse -Force | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
        Get-ChildItem -Path . -Include .pytest_cache -Recurse -Force | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "Clean complete." -ForegroundColor Green
    }
    Default {
        Show-Help
    }
}
