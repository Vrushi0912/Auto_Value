function updateProfile() {
    const newName = document.getElementById('updateFullNameInput').value;
    if (!newName || newName.length <= 5) {
        alert('Full Name should be more than 5 characters.');
        return;
    }
    
    fetch('/update-profile', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ full_name: newName })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        location.reload(); // Reload to see the updated name
    })
    .catch(error => console.error('Error:', error));
}

document.addEventListener('DOMContentLoaded', () => {
    // Smooth scrolling for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if(target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });

    // Mobile menu toggle
    const hamburger = document.querySelector('.hamburger');
    const navLinks = document.querySelector('.nav-links');
    
    if(hamburger) {
        hamburger.addEventListener('click', () => {
            // Simple toggle for demo purposes
            if (navLinks.style.display === 'flex') {
                navLinks.style.display = 'none';
            } else {
                navLinks.style.display = 'flex';
                navLinks.style.flexDirection = 'column';
                navLinks.style.position = 'absolute';
                navLinks.style.top = '100%';
                navLinks.style.left = '0';
                navLinks.style.width = '100%';
                navLinks.style.background = 'rgba(13, 15, 18, 0.95)';
                navLinks.style.padding = '2rem';
            }
        });
    }

    // Load data from API
    loadCars();
    loadBlogs();
});

async function loadCars() {
    try {
        const response = await fetch('/api/cars');
        const data = await response.json();
        
        if (data.status === 'success' && data.data.length > 0) {
            renderCars(data.data);
            populateComparisonSelects(data.data);
        }
    } catch (error) {
        console.error("Failed to load cars from API, using fallback data:", error);
        const fallbackCars = [
            {"CarName": "Maruti Suzuki Swift", "Price": "5.50 Lakh", "Year": "2019", "Location": "Mumbai", "ImageURL": "", "Source": "Cars24"},
            {"CarName": "Hyundai Creta", "Price": "12.80 Lakh", "Year": "2021", "Location": "Delhi", "ImageURL": "", "Source": "Spinny"},
            {"CarName": "Honda City", "Price": "9.20 Lakh", "Year": "2020", "Location": "Pune", "ImageURL": "", "Source": "Cars24"}
        ];
        renderCars(fallbackCars);
        populateComparisonSelects(fallbackCars);
    }
}

function renderCars(carsArray) {
    const carousel = document.querySelector('.carousel');
    if (carousel) {
        carousel.innerHTML = ''; // Clear static data
        carsArray.slice(0, 6).forEach(car => {
            const priceStr = car.Price ? car.Price : "Check Price";
            const styleTag = car.ImageURL ? `background-image: url('${car.ImageURL}'); background-size: cover;` : `background: linear-gradient(45deg, #1e1e1e, #333);`;
            
            const card = `
            <a href="${car.ListingURL || '#'}" target="_blank" style="text-decoration: none; color: inherit; display: block; outline: none;">
                <div class="auto-card">
                    <div class="auto-card-img-wrapper">
                        <div class="auto-card-img" style="${styleTag}"></div>
                        <div class="auto-card-img-overlay"></div>
                        <span class="auto-card-badge">Popular</span>
                    </div>
                    <div class="auto-card-body">
                        <h3 class="auto-card-title">${car.CarName}</h3>
                        <p style="color: var(--text-secondary); font-size: 0.85rem;">Location: ${car.Location || 'Unknown'}</p>
                        
                        <div class="auto-card-details">
                            <span class="auto-card-pill"><i class="fa-regular fa-calendar"></i> ${car.Year}</span>
                            <span class="auto-card-pill"><i class="fa-solid fa-gauge-high"></i> ${car.KilometersDriven || '50000'} km</span>
                            <span class="auto-card-pill"><i class="fa-solid fa-gas-pump"></i> ${car.FuelType || 'Petrol'}</span>
                        </div>
                        
                        <div class="auto-card-price-row">
                            <div class="auto-card-price">₹ ${priceStr}</div>
                            <span class="auto-card-btn">View Car</span>
                        </div>
                    </div>
                </div>
            </a>`;
            carousel.innerHTML += card;
        });
    }
}

async function loadBlogs() {
    try {
        const response = await fetch('/api/blogs');
        const data = await response.json();
        
        if (data.all_blogs && data.all_blogs.length > 0) {
            const blogGrid = document.querySelector('.blog-grid');
            if (blogGrid) {
                blogGrid.innerHTML = ''; // Clear static data
                
                const isBlogsPage = window.location.pathname.includes('car_blogs');
                const limit = isBlogsPage ? data.all_blogs.length : 2;
                
                data.all_blogs.slice(0, limit).forEach(blog => {
                    const styleTag = blog.imageurl ? `background-image: url('${blog.imageurl}'); background-size: cover;` : `background: linear-gradient(45deg, #2a2a2a, #111);`;
                    const card = `
                    <div class="blog-card glass-card">
                        <div class="blog-img" style="${styleTag}"></div>
                        <div class="blog-content">
                            <span class="tag">Blog</span>
                            <h4>${blog.title}</h4>
                            <p>${blog.description || 'Read more about this trend.'}</p>
                            <p style="color: var(--text-secondary); font-size: 0.8rem; margin-bottom: 1rem;">
                                <i class="fa-regular fa-clock"></i> ${blog.publisheddate || 'Recent'}
                            </p>
                            <a href="${blog.blogurl || '#'}" class="read-more" target="_blank">Read More <i class="fa-solid fa-arrow-right"></i></a>
                        </div>
                    </div>`;
                    blogGrid.innerHTML += card;
                });
            }
        }
    } catch (error) {
        console.error("Failed to load blogs from API:", error);
    }
}

// Mock Price Prediction Function
async function showPrediction() {
    const form = document.getElementById('prediction-form');
    const resultDiv = document.getElementById('predictionResult');
    const priceValueSpan = document.getElementById('priceValue');
    const btn = form.querySelector('button');
    
    // Simulate API Call Delay
    const originalText = btn.innerText;
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Analyzing Market...';
    btn.disabled = true;

    try {
        const formData = new FormData(form);
        const response = await fetch('/home/get-price-prediction', {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            const price = await response.text();
            priceValueSpan.innerText = price.replace('Lakhs', '').trim() || "5.00 Lakh";
            
            // Show the "See listings" button
            const seeListingsBtn = document.getElementById('view-similar-btn');
            if (seeListingsBtn) seeListingsBtn.style.display = 'block';
            
            // Store the values for the button action
            window.predictedCompany = form.querySelector('[name="select-company-price"]').value;
            window.predictedModel = form.querySelector('[name="select-model-price"]').value;
        } else {
            priceValueSpan.innerText = "Error";
        }
    } catch (error) {
        console.error("Prediction failed:", error);
        priceValueSpan.innerText = "5.00 Lakh";
    } finally {
        resultDiv.classList.remove('hidden');
        btn.innerHTML = originalText;
        btn.disabled = false;
        resultDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
}

function viewSimilarCars() {
    const company = window.predictedCompany || '';
    const model = window.predictedModel || '';
    
    // Scroll to search section
    const searchSection = document.getElementById('search');
    if (searchSection) {
        searchSection.scrollIntoView({ behavior: 'smooth' });
        
        // Fill the search form
        const searchForm = document.querySelector('.advanced-search-form');
        if (searchForm) {
            const companySelect = searchForm.querySelector('[name="select-company"]');
            const modelInput = searchForm.querySelector('[name="select-model"]');
            
            if (companySelect) companySelect.value = company.toLowerCase();
            if (modelInput) modelInput.value = model;
            
            // Wait 1 second for scroll to finish, then submit!
            setTimeout(() => {
                searchForm.submit();
            }, 1000);
        }
    }
}

let allLoadedCars = [];

function populateComparisonSelects(cars) {
    allLoadedCars = cars;
    const select1 = document.getElementById('select-car-1');
    const select2 = document.getElementById('select-car-2');
    
    if (!select1 || !select2) return;
    
    select1.innerHTML = '<option value="">Select a Car</option>';
    select2.innerHTML = '<option value="">Select a Car</option>';
    
    cars.forEach((car, index) => {
        const option = `<option value="${index}">${car.CarName} (${car.Source})</option>`;
        select1.innerHTML += option;
        select2.innerHTML += option;
    });
}

function updateComparison(slot) {
    const select = document.getElementById(`select-car-${slot}`);
    const index = select.value;
    const detailsDiv = document.getElementById(`details-car-${slot}`);
    
    if (!index) {
        detailsDiv.innerHTML = '<p>Select a car to see details</p>';
        document.getElementById(`header-car-${slot}`).innerText = `Car ${slot}`;
        document.getElementById(`price-car-${slot}`).innerText = '--';
        document.getElementById(`year-car-${slot}`).innerText = '--';
        document.getElementById(`km-car-${slot}`).innerText = '--';
        document.getElementById(`fuel-car-${slot}`).innerText = '--';
        document.getElementById(`source-car-${slot}`).innerText = '--';
        return;
    }
    
    const car = allLoadedCars[index];
    
    document.getElementById(`header-car-${slot}`).innerText = car.CarName;
    document.getElementById(`price-car-${slot}`).innerText = `₹ ${car.Price}`;
    document.getElementById(`year-car-${slot}`).innerText = car.Year;
    document.getElementById(`km-car-${slot}`).innerText = `${car.KilometersDriven || '50000'} km`;
    document.getElementById(`fuel-car-${slot}`).innerText = car.FuelType || 'Petrol';
    document.getElementById(`source-car-${slot}`).innerText = car.Source;
    
    detailsDiv.innerHTML = `
        <p style="font-weight: 600;">${car.CarName}</p>
        <p style="color: #5cb85c; font-weight: 600;">₹ ${car.Price}</p>
        <p style="font-size: 0.85rem; color: #666;">Source: ${car.Source}</p>
    `;
}

async function performSmartComparison() {
    const company = document.getElementById('compare-company').value;
    const model = document.getElementById('compare-model').value;
    const year = document.getElementById('compare-year').value;
    const fuel = document.getElementById('compare-fuel').value;
    const transmission = document.getElementById('compare-transmission').value;
    const location = document.getElementById('compare-location').value;
    
    const verdictTd = document.getElementById('comparison-verdict');
    verdictTd.innerText = "Searching for the best options...";
    
    try {
        const url = `/api/cars?company=${company}&model=${model}&year=${year}&fuel=${fuel}&transmission=${transmission}&location=${location}`;
        const response = await fetch(url);
        const data = await response.json();
        
        if (data.status === 'success' && data.data.length > 0) {
            const cars = data.data;
            
            // Find one from Cars24 and one from Spinny
            const cars24 = cars.find(c => (c.Source || c.source || '').toLowerCase() === 'cars24');
            const spinny = cars.find(c => (c.Source || c.source || '').toLowerCase() === 'spinny');
            
            updateCompareTable(cars24, spinny);
            
            // Calculate Verdict
            if (cars24 && spinny) {
                const p1 = parseFloat((cars24.Price || cars24.price || '0').replace('Lakh', '').trim());
                const p2 = parseFloat((spinny.Price || spinny.price || '0').replace('Lakh', '').trim());
                
                const y1 = parseInt(cars24.Year || cars24.year || '0');
                const y2 = parseInt(spinny.Year || spinny.year || '0');
                
                const km1 = parseInt(cars24.KilometersDriven || cars24.kilometersdriven || '0');
                const km2 = parseInt(spinny.KilometersDriven || spinny.kilometersdriven || '0');
                
                let score1 = 0;
                let score2 = 0;
                
                // Price factor (lower is better)
                if (p1 < p2) score1++;
                if (p2 < p1) score2++;
                
                // Year factor (newer is better)
                if (y1 > y2) score1++;
                if (y2 > y1) score2++;
                
                // KM factor (lower is better)
                if (km1 < km2) score1++;
                if (km2 < km1) score2++;
                
                let verdict = "";
                if (score1 > score2) {
                    verdict = "We recommend the **Cars24 option**. It scores better across price, year, and mileage!";
                    if (p1 > p2) verdict += " (Though it is slightly more expensive).";
                } else if (score2 > score1) {
                    verdict = "We recommend the **Spinny option**. It scores better across price, year, and mileage!";
                    if (p2 > p1) verdict += " (Though it is slightly more expensive).";
                } else {
                    // Tie breaker or specific callouts
                    if (p1 < p2) {
                        verdict = "It's a tie! Cars24 is cheaper, but Spinny might have a better year or mileage.";
                    } else if (p2 < p1) {
                        verdict = "It's a tie! Spinny is cheaper, but Cars24 might have a better year or mileage.";
                    } else {
                        verdict = "Both options are very similar! Choose based on your preference or location.";
                    }
                }
                
                // Add specific details to verdict
                verdict += ` <br><span style="font-size: 0.85rem; color: #666;">Cars24: ₹ ${p1}L, ${y1}, ${km1}km | Spinny: ₹ ${p2}L, ${y2}, ${km2}km</span>`;
                
                verdictTd.innerHTML = verdict;
            } else if (cars24) {
                verdictTd.innerText = "Only a Cars24 option was found matching your criteria.";
            } else if (spinny) {
                verdictTd.innerText = "Only a Spinny option was found matching your criteria.";
            } else {
                verdictTd.innerText = "No direct matches found from either source. Try broadening your search!";
            }
            
        } else {
            verdictTd.innerText = "No cars found matching your criteria. Try different filters!";
            updateCompareTable(null, null);
        }
    } catch (error) {
        console.error("Smart comparison failed:", error);
        verdictTd.innerText = "An error occurred. Please try again.";
    }
}

function updateCompareTable(c1, c2) {
    const setCell = (id, val) => document.getElementById(id).innerText = val || '--';
    const setCellHtml = (id, val) => document.getElementById(id).innerHTML = val || '--';
    
    if (c1) {
        document.getElementById('header-car-1').innerText = c1.CarName || c1.carname;
        setCell('name-car-1', c1.CarName || c1.carname);
        setCell('price-car-1', `₹ ${c1.Price || c1.price}`);
        setCell('year-car-1', c1.Year || c1.year);
        setCell('km-car-1', `${c1.KilometersDriven || c1.kilometersdriven || '50000'} km`);
        setCell('fuel-car-1', c1.FuelType || c1.fueltype);
        setCell('trans-car-1', c1.Transmission || c1.transmission || 'Manual');
        setCell('source-car-1', c1.Source || c1.source || 'Cars24');
        
        const img = c1.ImageURL || c1.imageurl;
        if (img) {
            setCellHtml('img-car-1', `<img src="${img}" style="width: 100%; max-width: 150px; border-radius: 8px;">`);
        } else {
            setCell('img-car-1', '--');
        }
        
        const url = c1.ListingURL || c1.listingurl;
        if (url) {
            setCellHtml('link-car-1', `<a href="${url}" target="_blank" class="btn-solid-green" style="padding: 0.3rem 0.8rem; font-size: 0.8rem;">View Car</a>`);
        } else {
            setCell('link-car-1', '--');
        }
    } else {
        document.getElementById('header-car-1').innerText = 'Cars24 Option';
        setCell('name-car-1', '--');
        setCell('price-car-1', '--');
        setCell('year-car-1', '--');
        setCell('km-car-1', '--');
        setCell('fuel-car-1', '--');
        setCell('trans-car-1', '--');
        setCell('source-car-1', '--');
        setCell('link-car-1', '--');
        setCell('img-car-1', '--');
    }
    
    if (c2) {
        document.getElementById('header-car-2').innerText = c2.CarName || c2.carname;
        setCell('name-car-2', c2.CarName || c2.carname);
        setCell('price-car-2', `₹ ${c2.Price || c2.price}`);
        setCell('year-car-2', c2.Year || c2.year);
        setCell('km-car-2', `${c2.KilometersDriven || c2.kilometersdriven || '50000'} km`);
        setCell('fuel-car-2', c2.FuelType || c2.fueltype);
        setCell('trans-car-2', c2.Transmission || c2.transmission || 'Manual');
        setCell('source-car-2', c2.Source || c2.source || 'Spinny');
        
        const img = c2.ImageURL || c2.imageurl;
        if (img) {
            setCellHtml('img-car-2', `<img src="${img}" style="width: 100%; max-width: 150px; border-radius: 8px;">`);
        } else {
            setCell('img-car-2', '--');
        }
        
        const url = c2.ListingURL || c2.listingurl;
        if (url) {
            setCellHtml('link-car-2', `<a href="${url}" target="_blank" class="btn-solid-green" style="padding: 0.3rem 0.8rem; font-size: 0.8rem;">View Car</a>`);
        } else {
            setCell('link-car-2', '--');
        }
    } else {
        document.getElementById('header-car-2').innerText = 'Spinny Option';
        setCell('name-car-2', '--');
        setCell('price-car-2', '--');
        setCell('year-car-2', '--');
        setCell('km-car-2', '--');
        setCell('fuel-car-2', '--');
        setCell('trans-car-2', '--');
        setCell('source-car-2', '--');
        setCell('link-car-2', '--');
        setCell('img-car-2', '--');
    }
}

// Car Finder Quiz Logic
let quizAnswers = {};
const totalSteps = 10;

function nextStep(currentStep, answer) {
    const keys = ['', 'budget', 'purpose', 'usage', 'transmission', 'fuel', 'bodyType', 'priority', 'duration', 'parking'];
    quizAnswers[keys[currentStep]] = answer;
    
    document.getElementById(`step-${currentStep}`).classList.add('hidden');
    document.getElementById(`step-${currentStep + 1}`).classList.remove('hidden');
    
    // Update progress bar
    const progress = ((currentStep + 1) / totalSteps) * 100;
    const progressBar = document.getElementById('quiz-progress');
    if (progressBar) progressBar.style.width = `${progress}%`;
}

function calculateResult(lastAnswer) {
    quizAnswers.maintenance = lastAnswer;
    document.getElementById('step-10').classList.add('hidden');
    document.getElementById('quiz-result').classList.remove('hidden');
    const progressBar = document.getElementById('quiz-progress');
    if (progressBar) progressBar.style.width = `100%`;
    
    const list = document.getElementById('recommendations-list');
    list.innerHTML = '';
    
    // Cars database with tags
    const cars = [
        { name: 'Maruti Alto', tags: ['under5', 'solo', 'city', 'manual', 'petrol', 'hatchback', 'efficiency', 'short', 'tight', 'low'] },
        { name: 'Tata Tiago', tags: ['under5', 'solo', 'city', 'manual', 'petrol', 'hatchback', 'safety', 'long', 'tight', 'low'] },
        { name: 'Maruti WagonR', tags: ['under5', 'family', 'city', 'manual', 'cng', 'hatchback', 'efficiency', 'short', 'tight', 'low'] },
        { name: 'Maruti Swift', tags: ['5to10', 'solo', 'city', 'manual', 'petrol', 'hatchback', 'performance', 'short', 'tight', 'low'] },
        { name: 'Hyundai i20', tags: ['5to10', 'solo', 'city', 'auto', 'petrol', 'hatchback', 'luxury', 'short', 'tight', 'medium'] },
        { name: 'Tata Nexon', tags: ['5to10', 'family', 'highway', 'manual', 'diesel', 'suv', 'safety', 'long', 'spacious', 'medium'] },
        { name: 'Maruti Brezza', tags: ['5to10', 'family', 'city', 'auto', 'petrol', 'suv', 'efficiency', 'long', 'spacious', 'low'] },
        { name: 'Hyundai Creta', tags: ['above10', 'family', 'highway', 'auto', 'petrol', 'suv', 'luxury', 'long', 'spacious', 'medium'] },
        { name: 'Mahindra XUV700', tags: ['above10', 'family', 'highway', 'auto', 'diesel', 'suv', 'performance', 'long', 'spacious', 'high'] },
        { name: 'Tata Harrier', tags: ['above10', 'family', 'highway', 'manual', 'diesel', 'suv', 'safety', 'long', 'spacious', 'high'] },
        { name: 'Mahindra Thar', tags: ['above10', 'solo', 'highway', 'auto', 'diesel', 'suv', 'performance', 'short', 'spacious', 'high'] },
        { name: 'Honda City', tags: ['above10', 'family', 'highway', 'auto', 'petrol', 'sedan', 'luxury', 'long', 'spacious', 'medium'] },
        { name: 'Tata Nexon EV', tags: ['above10', 'city', 'city', 'auto', 'electric', 'suv', 'efficiency', 'long', 'spacious', 'medium'] }
    ];
    
    // Score cars
    const scores = cars.map(car => {
        let score = 0;
        const userTags = Object.values(quizAnswers);
        userTags.forEach(tag => {
            if (car.tags.includes(tag)) score++;
        });
        return { name: car.name, score: score };
    });
    
    // Sort by score
    scores.sort((a, b) => b.score - a.score);
    
    // Get top 3
    const top3 = scores.slice(0, 3);
    
    top3.forEach(item => {
        const div = document.createElement('div');
        div.className = 'white-container';
        div.style.padding = '1.5rem';
        div.style.width = '200px';
        div.style.textAlign = 'center';
        div.style.border = '1px solid #eee';
        
        const parts = item.name.split(' ');
        const brand = parts[0];
        const model = parts.slice(1).join(' ');
        
        div.innerHTML = `
            <h4 style="color: #111; margin-bottom: 0.5rem;">${item.name}</h4>
            <span style="color: #4cae4c; font-weight: 600; font-size: 0.9rem;">Match: ${Math.round((item.score/10)*100)}%</span>
            <button class="btn-solid-green" style="padding: 0.3rem 0.8rem; font-size: 0.8rem; margin-top: 1rem; width: 100%;" onclick="searchCar('${brand}', '${model}')">See Listings</button>
        `;
        list.appendChild(div);
    });
}

function searchCar(brand, model) {
    const searchSection = document.getElementById('search');
    if (searchSection) {
        searchSection.scrollIntoView({ behavior: 'smooth' });
        
        const searchForm = document.querySelector('.advanced-search-form');
        if (searchForm) {
            const companySelect = searchForm.querySelector('[name="select-company"]');
            const modelInput = searchForm.querySelector('[name="select-model"]');
            
            if (companySelect) companySelect.value = brand.toLowerCase();
            if (modelInput) modelInput.value = model;
            
            // Wait 1 second for scroll to finish, then submit!
            setTimeout(() => {
                searchForm.submit();
            }, 1000);
        }
    }
}

function resetQuiz() {
    quizAnswers = {};
    document.getElementById('quiz-result').classList.add('hidden');
    document.getElementById('step-1').classList.remove('hidden');
    for (let i = 2; i <= 10; i++) {
        const step = document.getElementById(`step-${i}`);
        if (step) step.classList.add('hidden');
    }
    const progressBar = document.getElementById('quiz-progress');
    if (progressBar) progressBar.style.width = `10%`;
}
