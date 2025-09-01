// Configuration
    const config = {
      genders: ['m', 'f'],
      languages: [
        { code: 'en', name: 'English' },
        { code: 'slo', name: 'Slovenian' }
      ],
      sentences: [1, 2, 3, 4, 5],
      models: ['beatrice1', 'beatrice2', 'joker', 'maggie', 'monster', 'onnx'],
      ratings: [
        { id: 'dissimilarity', label: 'Dissimilarity' },
        { id: 'naturalness', label: 'Naturalness' },
        { id: 'pronunciation', label: 'Pronunciation' },
        { id: 'audioQuality', label: 'Audio Quality' },
      ]
    };

    function updateValue(slider, spanId) {
      document.getElementById(spanId).textContent = slider.value;
    }

    function generateSurvey() {
      const container = document.getElementById('survey-container');
      let sectionIndex = 0;
      
      config.genders.forEach(gender => {
        config.languages.forEach(language => {
          config.sentences.forEach(sentence => {
            sectionIndex++;
            
            const genderName = gender === 'm' ? 'Male' : 'Female';
            const referenceAudio = `inputs/${gender}/input_${language.code}_${sentence}.wav`;
            
            // Create section
            const section = document.createElement('div');
            section.className = 'bg-white shadow rounded-xl p-6 mb-8 border border-pink-200';
            
            // Section header
            const header = document.createElement('h2');
            header.className = 'text-lg font-semibold mb-4 text-pink-800';
            header.textContent = `Sentence ${sentence} – ${genderName} – ${language.name}`;
            section.appendChild(header);
            
            // Reference audio
            const refDiv = document.createElement('div');
            refDiv.className = 'mb-6';
            refDiv.innerHTML = `
              <p class="mb-1 text-pink-700">Reference voice:</p>
              <audio controls class="w-64">
                <source src="${referenceAudio}" type="audio/wav">
              </audio>
            `;
            section.appendChild(refDiv);
            
            // Desktop layout
            const desktopDiv = document.createElement('div');
            desktopDiv.className = 'hidden lg:block';
            
            const desktopGrid = document.createElement('div');
            desktopGrid.className = 'grid grid-cols-7 gap-4';
            
            // Labels column for desktop
            const labelsCol = document.createElement('div');
            labelsCol.className = 'col-span-1';
            labelsCol.innerHTML = `
              <div class="h-12 mb-4"></div>
              <div class="space-y-8">
                ${config.ratings.map(rating => `
                  <div class="flex items-center h-5">
                    <label class="text-sm font-medium text-pink-700">${rating.label}</label>
                  </div>
                `).join('')}
              </div>
            `;
            desktopGrid.appendChild(labelsCol);
            
            // Model columns for desktop
            config.models.forEach((model, modelIndex) => {
              const modelAudio = `data/${gender}/${model}/monitor_${language.code}_${sentence}.wav`;
              const modelCol = document.createElement('div');
              modelCol.className = 'col-span-1 flex flex-col items-center';
              
              const slidersHtml = config.ratings.map(rating => {
                const inputName = `${rating.id}_${model}_s${sectionIndex}`;
                const valueId = `${inputName}_value`;
                return `
                  <div class="flex items-center space-x-2">
                    <input type="range" min="0" max="10" value="5" step="1" name="${inputName}" 
                           class="flex-1 accent-pink-500" oninput="updateValue(this, '${valueId}')">
                    <span id="${valueId}" class="text-sm font-medium w-6 text-pink-700">5</span>
                  </div>
                `;
              }).join('');
              
              modelCol.innerHTML = `
                <audio controls class="w-36 mb-4 audio_style">
                  <source src="${modelAudio}" type="audio/wav">
                </audio>
                <div class="space-y-8 w-full">
                  ${slidersHtml}
                </div>
              `;
              
              desktopGrid.appendChild(modelCol);
            });
            
            desktopDiv.appendChild(desktopGrid);
            section.appendChild(desktopDiv);
            
            // Mobile layout
            const mobileDiv = document.createElement('div');
            mobileDiv.className = 'block lg:hidden space-y-6';
            
            config.models.forEach((model, modelIndex) => {
              const modelAudio = `data/${gender}/${model}/monitor_${language.code}_${sentence}.wav`;
              const modelCard = document.createElement('div');
              
              const modelName = model.replace('_', ' ').toUpperCase();
              const mobileSlidersHtml = config.ratings.map(rating => {
                const inputName = `${rating.id}_${model}_s${sectionIndex}_mobile`;
                const valueId = `${inputName}_value`;
                return `
                  <div class="flex flex-wrap  items-center space-x-3">
                    <label class="w-64 text-pink-700">${rating.label}</label>
                    <input type="range" min="0" max="10" value="5" step="1" name="${inputName}" 
                           class="flex-1 accent-pink-500" oninput="updateValue(this, '${valueId}')">
                    <span id="${valueId}" class="flex justify-center w-12 text-pink-700">5</span>
                  </div>
                `;
              }).join('');
              
              modelCard.innerHTML = `
              <div class="${modelIndex % 2 === 0 ? 'bg-pink-50' : ''} p-4 rounded-lg border border-pink-200">
                <div class="flex justify-center mb-4" style="align-items: center;">
                  <h4 style="margin-right: 15px">${modelIndex + 1}.</h4>
                  <audio controls class="w-64 audio_style">
                    <source src="${modelAudio}" type="audio/wav">
                  </audio>
                </div>
                <div class="space-y-4">
                  ${mobileSlidersHtml}
                </div>
              </div>
              `;
              
              mobileDiv.appendChild(modelCard);
            });
            
            section.appendChild(mobileDiv);
            container.appendChild(section);
          });
        });
      });
    }

    function submitSurvey() {
      // Collect all form data
      const formData = {};
      const inputs = document.querySelectorAll('input[type="range"]');
      
      inputs.forEach(input => {
        formData[input.name] = parseInt(input.value);
      });

      // Group ratings by section/model
      const groupedData = {};
      Object.keys(formData).forEach(key => {
        if (key.includes('_mobile')) return; // skip mobile duplicates
        
        const parts = key.split('_');
        const rating = parts[0];   // e.g., "dissimilarity"
        const model = parts[1];    // e.g., "ModelA"
        const sectionKey = parts[2]; // e.g., "s1"
        
        if (!groupedData[sectionKey]) groupedData[sectionKey] = {};
        if (!groupedData[sectionKey][model]) groupedData[sectionKey][model] = {};
        
        groupedData[sectionKey][model][rating] = formData[key];
      });

      // Generate section metadata
      const sectionMetadata = {};
      let sectionIndex = 0;
      config.genders.forEach(gender => {
        config.languages.forEach(language => {
          config.sentences.forEach(sentence => {
            sectionIndex++;
            const sectionKey = `s${sectionIndex}`;
            const genderName = gender === "m" ? "Male" : "Female";
            sectionMetadata[sectionKey] = {
              section: sectionKey,
              gender: genderName,
              language: language.code,
              sentence: sentence
            };
          });
        });
      });

      // Flatten into list of row objects
      const rows = [];
      Object.keys(groupedData).forEach(sectionKey => {
        const sectionData = groupedData[sectionKey];
        const metadata = sectionMetadata[sectionKey];

        config.models.forEach(model => {
          if (sectionData[model]) {
            rows.push({
              section: metadata.section,
              gender: metadata.gender,
              language: metadata.language,
              model: model,
              dissimilarity: sectionData[model].dissimilarity || 5,
              naturalness: sectionData[model].naturalness || 5,
              pronunciation: sectionData[model].pronunciation || 5,
              audioQuality: sectionData[model].audioQuality || 5
            });
          }
        });
      });

      console.log("Survey rows:", rows);

      // Send all rows in one request
      sendToGoogleSheets(rows);
    }

    async function sendToGoogleSheets(sheetsData) {
      const GOOGLE_SCRIPT_URL =
        "https://script.google.com/macros/s/AKfycbxdN7mOkBdJ_U24sDcVhBZzrtblCoQfKJkNoW9ukpykbBQRNhrCeS60yWtURyBVLGvE/exec";

      try {
        const overlay = document.getElementById("loaderOverlay");
        const waitingText = document.getElementById("waiting");
        const finishedText = document.getElementById("finished");
        const spinner = document.getElementById("spinner");

        // Show overlay before upload
        overlay.style.display = "flex";
        finishedText.style.display = "none";

        // One single POST request with the array
        await fetch(GOOGLE_SCRIPT_URL, {
          method: "POST",
          mode: "no-cors", // Apps Script requires this for public web app
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(sheetsData),
        });

        waitingText.style.display = "none";
        spinner.style.display = "none";
        finishedText.style.display = "block";
      } catch (err) {
        alert("❌ Error submitting survey: " + err);
      }
    }

    // Generate the survey when page loads
    document.addEventListener('DOMContentLoaded', generateSurvey);