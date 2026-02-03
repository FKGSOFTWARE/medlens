# GitHub Setup Instructions

## Create Repository

1. Go to https://github.com/new
2. Repository name: `medlens`
3. Description: "3-Agent Clinical Image Analysis powered by MedGemma 4B"
4. **Public** (required for competition)
5. Don't initialize with README (we already have one)
6. Create repository

## Push Local Code

```bash
cd ~/medlens

# Add remote (replace FKGSOFTWARE)
git remote add origin https://github.com/FKGSOFTWARE/medlens.git

# Push
git branch -M main
git push -u origin main
```

## Verify

- [ ] Repository is public
- [ ] README displays correctly
- [ ] All source files present in `src/medlens/`
- [ ] Sample outputs in `examples/`
- [ ] Scripts in `scripts/`
- [ ] Tests in `tests/`

## Update Links

After pushing, update these files with the actual repo URL:

1. `docs/writeup_template.md` — line with `github.com/your-org/medlens`
2. `README.md` — line with `github.com/<your-org>/medlens`

```bash
# Example (replace with your actual username)
sed -i 's|github.com/your-org/medlens|github.com/ralphington/medlens|g' docs/writeup_template.md
sed -i 's|github.com/<your-org>/medlens|github.com/ralphington/medlens|g' README.md
git add docs/writeup_template.md README.md
git commit -m "Update GitHub repo links"
git push
```

## Add Topics (Optional)

On GitHub, click the gear icon next to "About" and add topics:
- `medgemma`
- `clinical-ai`
- `healthcare`
- `multimodal`
- `streamlit`
- `kaggle-competition`
