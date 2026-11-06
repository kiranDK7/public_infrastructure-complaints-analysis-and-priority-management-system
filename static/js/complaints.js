/**
 * SMART CIVICCARE 2.0 - DYNAMIC AI PRE-TRIAGE & DUPLICATE DETECTOR
 * Supports English & Kannada text inputs.
 */

let aiDebounceTimer = null;

function setupDynamicAITriage() {
  const titleInput = document.getElementById('inputTitle');
  const descInput = document.getElementById('inputDescription');
  const sevInput = document.getElementById('selectSeverity');
  const catInput = document.getElementById('selectCategory');
  const latInput = document.getElementById('inputLat');
  const lngInput = document.getElementById('inputLng');
  const wardInput = document.getElementById('selectWard');

  if (!titleInput || !descInput) return;

  function runAITriage() {
    const title = titleInput.value.trim();
    const desc = descInput.value.trim();

    if (title.length < 4 && desc.length < 8) return;

    const payload = {
      title: title,
      description: desc,
      severity: sevInput ? sevInput.value : 'Medium',
      latitude: latInput ? latInput.value : 12.9716,
      longitude: lngInput ? lngInput.value : 77.5946,
      ward: wardInput ? wardInput.value : 'Ward 42'
    };

    const aiBox = document.getElementById('aiPreTriageBox');
    const spinner = document.getElementById('aiSpinner');
    if (spinner) spinner.classList.remove('d-none');

    fetch('/api/ai/analyze-complaint', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
      .then(res => res.json())
      .then(data => {
        if (spinner) spinner.classList.add('d-none');
        if (!data.success) return;

        if (aiBox) aiBox.classList.remove('d-none');

        // Update Suggested Department & Category
        const catPill = document.getElementById('aiSuggestedCat');
        const deptPill = document.getElementById('aiSuggestedDept');
        const catConf = document.getElementById('aiCatConfidence');

        if (catPill) catPill.innerText = data.classification.suggested_category;
        if (deptPill) deptPill.innerText = `Department: ${data.classification.suggested_department || data.classification.suggested_category}`;
        if (catConf) catConf.innerText = `${data.classification.confidence_pct}% Match`;

        // Update Priority & Risk Score
        const priPill = document.getElementById('aiSuggestedPriority');
        const priScore = document.getElementById('aiPriorityScore');
        const priExplanation = document.getElementById('aiPriorityExplanation');
        const priSLA = document.getElementById('aiRecommendedSLA');

        if (priPill) {
          priPill.innerText = data.priority.level;
          priPill.className = 'badge ' + (
            data.priority.level === 'HIGH' ? 'badge-priority-high' :
            (data.priority.level === 'MEDIUM' ? 'badge-priority-medium' : 'badge-priority-low')
          );
        }
        if (priScore) priScore.innerText = `${data.priority.score}/100`;
        if (priExplanation) priExplanation.innerText = data.priority.explanation;
        if (priSLA && data.priority.recommended_sla_hours) {
          priSLA.innerText = `Target SLA: ${data.priority.recommended_sla_hours}h Response`;
        }

        // Keywords
        const kwContainer = document.getElementById('aiKeywordsDetected');
        if (kwContainer && data.classification.keywords) {
          kwContainer.innerHTML = data.classification.keywords.map(kw =>
            `<span class="badge bg-light text-secondary border me-1">${kw}</span>`
          ).join('') || '<span class="text-muted small">None</span>';
        }

        // Duplicate Warning
        const dupWarning = document.getElementById('aiDuplicateWarning');
        if (dupWarning) {
          if (data.duplicate && data.duplicate.is_duplicate) {
            dupWarning.classList.remove('d-none');
            dupWarning.innerHTML = `
              <div class="alert alert-warning border-0 shadow-sm d-flex align-items-start gap-2 mb-0">
                <i class="bi bi-exclamation-triangle-fill fs-5 text-warning flex-shrink-0"></i>
                <div>
                  <strong class="d-block">Related Incident Detected Nearby!</strong>
                  <div class="small mt-1">${data.duplicate.advisory}</div>
                  <div class="small text-muted mt-1">NLP Match: ${data.duplicate.similarity_pct}% | Distance: ${data.duplicate.distance_meters}m</div>
                </div>
              </div>
            `;
          } else {
            dupWarning.classList.add('d-none');
          }
        }
      })
      .catch(err => {
        if (spinner) spinner.classList.add('d-none');
        console.error('AI Triage error:', err);
      });
  }

  window.triggerAIAnalysis = function() {
    clearTimeout(aiDebounceTimer);
    aiDebounceTimer = setTimeout(runAITriage, 400);
  };

  titleInput.addEventListener('input', window.triggerAIAnalysis);
  descInput.addEventListener('input', window.triggerAIAnalysis);
  if (sevInput) sevInput.addEventListener('change', window.triggerAIAnalysis);
  if (wardInput) wardInput.addEventListener('change', window.triggerAIAnalysis);

  // Apply button
  const acceptBtn = document.getElementById('btnAcceptAICat');
  if (acceptBtn && catInput) {
    acceptBtn.addEventListener('click', function() {
      const suggestedCat = document.getElementById('aiSuggestedCat').innerText;
      if (suggestedCat && suggestedCat !== '--') {
        catInput.value = suggestedCat;
        acceptBtn.innerHTML = '<i class="bi bi-check-circle me-1"></i>Applied';
        setTimeout(() => { acceptBtn.innerHTML = 'Apply Suggestion'; }, 2000);
      }
    });
  }
}

document.addEventListener('DOMContentLoaded', setupDynamicAITriage);

