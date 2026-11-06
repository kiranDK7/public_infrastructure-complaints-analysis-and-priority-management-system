/**
 * Citizen Portal Dynamic AI Pre-Triage Assistant
 */

let debounceTimer = null;

function setupAIAnalysis() {
  const titleInput = document.getElementById('inputTitle');
  const descInput = document.getElementById('inputDescription');
  const sevInput = document.getElementById('selectSeverity');
  const catInput = document.getElementById('selectCategory');
  const latInput = document.getElementById('inputLat');
  const lngInput = document.getElementById('inputLng');

  if (!titleInput || !descInput) return;

  function runAnalysis() {
    const title = titleInput.value.trim();
    const desc = descInput.value.trim();

    if (title.length < 5 && desc.length < 10) return;

    const payload = {
      title: title,
      description: desc,
      severity: sevInput ? sevInput.value : 'Medium',
      latitude: latInput ? latInput.value : 12.9716,
      longitude: lngInput ? lngInput.value : 77.5946
    };

    const aiCard = document.getElementById('aiSuggestionBox');
    const aiSpinner = document.getElementById('aiSpinner');
    if (aiSpinner) aiSpinner.classList.remove('d-none');

    fetch('/api/ai/analyze-complaint', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
      .then(res => res.json())
      .then(data => {
        if (aiSpinner) aiSpinner.classList.add('d-none');
        if (!data.success) return;

        if (aiCard) aiCard.classList.remove('d-none');

        // Update Category Suggestion
        const catPill = document.getElementById('aiSuggestedCat');
        const catConf = document.getElementById('aiCatConfidence');
        if (catPill) catPill.innerText = data.classification.suggested_category;
        if (catConf) catConf.innerText = `${data.classification.confidence_pct}% Match`;

        // Update Priority Suggestion
        const priPill = document.getElementById('aiSuggestedPriority');
        const priScore = document.getElementById('aiPriorityScore');
        const priExplanation = document.getElementById('aiPriorityExplanation');
        
        if (priPill) {
          priPill.innerText = data.priority.level;
          priPill.className = 'badge ' + (
            data.priority.level === 'HIGH' ? 'badge-priority-high' :
            (data.priority.level === 'MEDIUM' ? 'badge-priority-medium' : 'badge-priority-low')
          );
        }
        if (priScore) priScore.innerText = `${data.priority.score}/100`;
        if (priExplanation) priExplanation.innerText = data.priority.explanation;

        // Keywords detected
        const kwContainer = document.getElementById('aiKeywordsDetected');
        if (kwContainer && data.classification.keywords) {
          kwContainer.innerHTML = data.classification.keywords.map(kw => 
            `<span class="badge bg-light text-secondary border me-1">${kw}</span>`
          ).join('') || '<span class="text-muted small">None</span>';
        }

        // Duplicate Advisory Alert
        const dupAlert = document.getElementById('aiDuplicateWarning');
        if (dupAlert) {
          if (data.duplicate.is_duplicate) {
            dupAlert.classList.remove('d-none');
            dupAlert.innerHTML = `
              <div class="alert alert-warning border-0 shadow-sm d-flex align-items-start gap-2 mb-0">
                <i class="bi bi-exclamation-triangle-fill fs-5 text-warning flex-shrink-0"></i>
                <div>
                  <strong>Potential Duplicate Issue Detected!</strong>
                  <div class="small mt-1">${data.duplicate.advisory}</div>
                  <div class="small text-muted mt-1">Similarity: ${data.duplicate.similarity_pct}% | Proximity: ${data.duplicate.distance_meters}m</div>
                </div>
              </div>
            `;
          } else {
            dupAlert.classList.add('d-none');
          }
        }
      })
      .catch(err => {
        if (aiSpinner) aiSpinner.classList.add('d-none');
        console.error('AI Pre-Triage Error:', err);
      });
  }

  window.triggerAIAnalysis = function () {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(runAnalysis, 450);
  };

  titleInput.addEventListener('input', window.triggerAIAnalysis);
  descInput.addEventListener('input', window.triggerAIAnalysis);
  if (sevInput) sevInput.addEventListener('change', window.triggerAIAnalysis);

  // Accept suggestion button
  const acceptBtn = document.getElementById('btnAcceptAICat');
  if (acceptBtn && catInput) {
    acceptBtn.addEventListener('click', function () {
      const suggestedCat = document.getElementById('aiSuggestedCat').innerText;
      if (suggestedCat) {
        catInput.value = suggestedCat;
        acceptBtn.innerHTML = '<i class="bi bi-check-circle me-1"></i>Applied';
        setTimeout(() => {
          acceptBtn.innerHTML = 'Apply Suggestion';
        }, 2000);
      }
    });
  }

  // Image Preview Handler
  const photoInput = document.getElementById('inputPhoto');
  const previewImg = document.getElementById('photoPreview');
  const previewBox = document.getElementById('photoPreviewBox');

  if (photoInput && previewImg && previewBox) {
    photoInput.addEventListener('change', function () {
      const file = this.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
          previewImg.src = e.target.result;
          previewBox.classList.remove('d-none');
        };
        reader.readAsDataURL(file);
      } else {
        previewBox.classList.add('d-none');
      }
    });
  }
}

document.addEventListener('DOMContentLoaded', setupAIAnalysis);

