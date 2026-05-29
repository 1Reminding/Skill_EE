---
name: pptx
description: "Presentation creation, editing, and analysis. Tasks include creating new presentations, modifying content, working with layouts, and adding comments/notes."
license: Proprietary. LICENSE.txt has complete terms
---

# PPTX creation, editing, and analysis

## Capability and use cases
- **Analysis**: Extract text, speaker notes, comments, and design metadata from .pptx files.
- **Creation (Scratch)**: Generate presentations using HTML/JS (html2pptx) for precise positioning.
- **Creation (Template)**: Duplicate and modify existing slide layouts using inventory/replacement workflows.
- **Editing**: Direct OOXML manipulation for complex formatting, animations, and master slides.

## Required artifacts
- **Documentation**: `html2pptx.md`, `ooxml.md` (Read fully; do not use range limits).
- **Scripts**: `unpack.py`, `pack.py`, `validate.py`, `rearrange.py`, `inventory.py`, `replace.py`, `thumbnail.py`, `html2pptx.js`.

## API/tool patterns
- **Text Extraction**: `python -m markitdown file.pptx`
- **OOXML Unpack**: `python ooxml/scripts/unpack.py <file> <dir>`
- **Thumbnail Grid**: `python scripts/thumbnail.py <file> <prefix> --cols 4` (Range: 3-6)
- **Rearrange**: `python scripts/rearrange.py <src> <dest> 0,34,34,50` (0-indexed)
- **Inventory**: `python scripts/inventory.py <file> <output.json>`
- **Replace**: `python scripts/replace.py <working.pptx> <replacements.json> <output.pptx>`
- **PDF Conversion**: `soffice --headless --convert-to pdf <file>`

## Implementation anchors
- **XML Paths**: `ppt/presentation.xml` (metadata), `ppt/slides/slide{N}.xml` (content), `ppt/notesSlides/` (notes), `ppt/theme/` (colors/fonts).
- **Design Constraints**: Use web-safe fonts (Arial, Helvetica, Times New Roman, Georgia, Courier New, Verdana, Tahoma, Trebuchet MS, Impact).
- **Dimensions**: Standard 16:9 is 720pt x 405pt.
- **Replacement JSON Schema**:
```json
{
  "slide-0": {
    "shape-0": {
      "paragraphs": [
        { "text": "Title", "bold": true, "alignment": "CENTER" },
        { "text": "Bullet", "bullet": true, "level": 0 }
      ]
    }
  }
}
```
- **Color Palettes**: Classic Blue (#1C2833, #2E4053), Teal/Coral (#5EA8A7, #FE4447), Burgundy (#5D1D2E, #997929), Sage/Terracotta (#87A96B, #E07A5F), Charcoal/Red (#292929, #E33737).

## Workflow
### 1. Template-Based Creation
1. Generate thumbnail grid and extract text via `markitdown`.
2. Create `template-inventory.md` (0-indexed list of all slides/layouts).
3. Map content to layouts in `outline.md`. Match column counts exactly to content items.
4. Run `rearrange.py` to build the slide sequence.
5. Run `inventory.py` to get shape IDs. **Note**: Shapes not in replacement JSON are cleared.
6. Create `replacement-text.json` preserving original paragraph properties (bold, size, color).
7. Apply via `replace.py` and verify with `thumbnail.py`.

### 2. HTML2PPTX (Scratch)
1. Define design approach (tone, branding, palette) before coding.
2. Create HTML slides. Use `class="placeholder"` for charts/tables.
3. Rasterize gradients/icons as PNG via Sharp before referencing in HTML.
4. Use `html2pptx.js` + `PptxGenJS` to render. Prefer two-column layouts for charts.

### 3. OOXML Editing
1. Unpack .pptx.
2. Edit XML (e.g., `ppt/slides/slide1.xml`).
3. **Validate** immediately: `python ooxml/scripts/validate.py <dir> --original <file>`.
4. Pack directory.

## Validation checks
- **Visual**: Check thumbnails for text cutoff, overlap, or low contrast.
- **Structural**: `replace.py` validates shape/slide existence and overflow delta.
- **OOXML**: `validate.py` must pass after every XML edit.

## Pitfalls
- **Do not** set range limits when reading `html2pptx.md`, `ooxml.md`, or `inventory.json`.
- **Do not** vertically stack charts/tables below text; use two-column or full-slide layouts.
- **Do not** include bullet symbols (•, -) in replacement text; use `"bullet": true`.
- **Do not** set `alignment` on paragraphs where `"bullet": true` (auto-left aligned).
- **Do not** reference non-existent shapes in `replacement-text.json`.