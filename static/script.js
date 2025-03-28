document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('ideaForm');
    const results = document.getElementById('results');
    const loading = document.getElementById('loading');
    const ideasList = document.getElementById('ideasList');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Show loading state
        loading.classList.remove('hidden');
        results.classList.add('hidden');
        
        // Get form data
        const formData = new FormData(form);
        const data = {
            difficulty: formData.get('difficulty'),
            timeFrame: formData.get('timeFrame'),
            numIdeas: parseInt(formData.get('numIdeas')),
            keywords: formData.get('keywords').split(',').map(k => k.trim()).filter(k => k),
            randomness: parseFloat(formData.get('randomness'))
        };

        try {
            const response = await fetch('/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();
            
            if (result.error) {
                throw new Error(result.error);
            }

            // Display results
            displayIdeas(result.ideas);
            results.classList.remove('hidden');
        } catch (error) {
            alert('Error generating ideas: ' + error.message);
        } finally {
            loading.classList.add('hidden');
        }
    });

    function displayIdeas(ideas) {
        ideasList.innerHTML = '';
        
        // Ideas are already JSON objects, no need to parse
        ideas.forEach(idea => {
            const ideaCard = document.createElement('div');
            ideaCard.className = 'bg-white rounded-lg shadow-lg p-6';
            
            ideaCard.innerHTML = `
                <h3 class="text-xl font-semibold text-gray-800 mb-2">${idea.title}</h3>
                <p class="text-gray-600 mb-4">${idea.description}</p>
                <div class="mb-4">
                    <h4 class="font-medium text-gray-700">Key Concepts:</h4>
                    <p class="text-gray-600">${idea.technical_concepts}</p>
                </div>
                <div>
                    <h4 class="font-medium text-gray-700">Estimated Time:</h4>
                    <p class="text-gray-600">${idea.estimated_time}</p>
                </div>
            `;
            
            ideasList.appendChild(ideaCard);
        });
    }
}); 