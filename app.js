document.addEventListener('DOMContentLoaded', () => {
    // Initialize API Gateway Client
    const apigClient = apigClientFactory.newClient();

    // Search Functionality
    document.getElementById('search-button').addEventListener('click', async () => {
        const query = document.getElementById('search-query').value;

        if (!query) {
            alert('Please enter a search query!');
            return;
        }

        try {
            const response = await apigClient.searchGet(
                { q: query },
                {},
                { headers: { 'x-api-key': 'cFcass5DO99FZldy6BeWaavyjtMrMKfDaC8cCeoe' } }
            );

            console.log('API Response:', response);

            // Parse the response body as JSON
            const parsedBody = JSON.parse(response.data.body);
            const results = parsedBody.results; // Access the "results" array
            console.log('Parsed API Results:', results);

            const resultsDiv = document.getElementById('search-results');
            resultsDiv.innerHTML = ''; // Clear old results

            // Handle no results
            if (!results || results.length === 0) {
                resultsDiv.innerHTML = '<p>No results found.</p>';
                return;
            }

            // Render each result
            results.forEach(result => {
                const img = document.createElement('img');
                img.src = `https://${result.source.bucket}.s3.amazonaws.com/${result.source.objectKey}`;
                img.alt = 'Photo';
                img.classList.add('search-result-img'); 
                resultsDiv.appendChild(img);
            });
        } catch (error) {
            console.error('Error fetching search results:', error);
            alert('Failed to fetch search results.');
        }
    });
//upload fucntionality
document.getElementById('upload-form').addEventListener('submit', async (e) => {
        e.preventDefault();

        const photoInput = document.getElementById('photo');
        const labelsInput = document.getElementById('custom-labels');

        if (!photoInput.files.length) {
            alert('Please select a file.');
            return;
        }

        const file = photoInput.files[0];
        const labels = labelsInput.value;
        console.log("file name is "+file.name);
        try {
            // Step 1: Get a presigned URL from the API Gateway
            const response = await apigClient.uploadPut(
                { key: file.name },
                file,
                {
                    headers: {
                        'x-api-key': 'cFcass5DO99FZldy6BeWaavyjtMrMKfDaC8cCeoe' ,
                        'Content-Type': file.type,
                    }
                }
            );
            console.log('Upload response:', response);
            alert('Photo uploaded successfully!');
        } catch (error) {
            console.error('Error uploading photo:', error);
            alert('Upload failed.');
        }
    });
});

