# Sample Clinical Images for Demo

MedLens demos should use **public domain or appropriately licensed** clinical images.

## Recommended Sources

### ISIC Archive (Dermatology)
- https://www.isic-archive.com/
- Over 70,000 dermoscopy images
- CC-BY license for most images
- Search for "melanoma", "nevus", "seborrheic keratosis"

### DermNet NZ
- https://dermnetnz.org/
- Educational use permitted with attribution
- High-quality clinical photos

### Fitzpatrick17k (Diverse Skin Tones)
- https://github.com/mattgroh/fitzpatrick17k
- Research dataset with Fitzpatrick scale annotations
- Good for demonstrating performance across skin types

## Demo Image Selection

For the competition demo, select images that show:

1. **Clear pathology** — visually interesting findings for the visual agent
2. **Moderate complexity** — not so obvious that reasoning is trivial
3. **Educational value** — demonstrates the pipeline's clinical utility

## Suggested Cases

| Case | Source | Why |
|------|--------|-----|
| Pigmented lesion with ABCDE features | ISIC | Shows morphology, color, border analysis |
| Wound with multiple tissue types | Public wound dataset | Shows severity, staging assessment |
| Rash with distribution pattern | DermNet | Shows anatomical location reasoning |

## Attribution

Always include attribution in the demo video and any published materials:

> "Sample images from the ISIC Archive (https://isic-archive.com), licensed under CC-BY."
