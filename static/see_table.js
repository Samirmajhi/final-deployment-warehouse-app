window.addEventListener('DOMContentLoaded', function() {
    const perPage = 10;
    let currentPage = 1;

    function fetchProducts(page) {
        fetch(`http://127.0.0.1:5000/products?page=${page}&per_page=${perPage}`)
        .then(response => response.json())
        .then(data => {
            console.log('Data received from API:', data);
            let tableBody = document.getElementById('productsTableBody');
            tableBody.innerHTML = '';
            data.products.forEach(product => {
                let row = document.createElement('tr');
                row.innerHTML = `
                    <td>${product.scan_id}</td>
                    <td>${product.EAN_13}</td>
                    <td>${product.Product_Name}</td> 
                    <td>${product.Product_Quantity}</td> 
                    <td>${product.Status}</td>
                    <td>${product.timestamp}</td>
                `;
                tableBody.appendChild(row);
            });
            setupPagination(data.total_pages, data.current_page);
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }

    function setupPagination(totalPages, currentPage) {
        const pagination = document.getElementById('pagination');
        pagination.innerHTML = '';

        if (totalPages > 1) {
            if (currentPage > 1) {
                const prevButton = document.createElement('button');
                prevButton.innerText = 'Previous';
                prevButton.addEventListener('click', () => fetchProducts(currentPage - 1));
                pagination.appendChild(prevButton);
            }

            for (let i = 1; i <= totalPages; i++) {
                const pageButton = document.createElement('button');
                pageButton.innerText = i;
                pageButton.disabled = i === currentPage;
                pageButton.addEventListener('click', () => fetchProducts(i));
                pagination.appendChild(pageButton);
            }

            if (currentPage < totalPages) {
                const nextButton = document.createElement('button');
                nextButton.innerText = 'Next';
                nextButton.addEventListener('click', () => fetchProducts(currentPage + 1));
                pagination.appendChild(nextButton);
            }
        }
    }

    fetchProducts(currentPage);
});
