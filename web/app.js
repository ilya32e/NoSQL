// Simulated data - In production, this would connect to your Python backend
let orders = [];
let drivers = [];

// Initialize dashboard
document.addEventListener('DOMContentLoaded', () => {
    loadMockData();
    updateStats();
    renderOrders();
    renderDrivers();
    startRealTimeUpdates();
});

// Load mock data
function loadMockData() {
    orders = [
        { id: 'c1', client: 'Client A', destination: 'Marais', amount: 25, status: 'pending', time: '14:00' },
        { id: 'c2', client: 'Client B', destination: 'Belleville', amount: 15, status: 'assigned', driver: 'd1', time: '14:05' },
        { id: 'c3', client: 'Client C', destination: 'Bercy', amount: 30, status: 'delivered', time: '14:10' },
        { id: 'c4', client: 'Client D', destination: 'Auteuil', amount: 20, status: 'pending', time: '14:15' },
        { id: 'c5', client: 'Client E', destination: 'Montmartre', amount: 18, status: 'assigned', driver: 'd2', time: '14:20' },
        { id: 'c6', client: 'Client F', destination: 'Bastille', amount: 22, status: 'pending', time: '14:25' },
    ];

    drivers = [
        { id: 'd1', name: 'Alice Dupont', region: 'Paris', rating: 4.8, deliveries: 156, revenue: 3420 },
        { id: 'd2', name: 'Bob Martin', region: 'Paris', rating: 4.5, deliveries: 142, revenue: 3180 },
        { id: 'd3', name: 'Charlie Lefevre', region: 'Banlieue', rating: 4.9, deliveries: 178, revenue: 3890 },
        { id: 'd4', name: 'Diana Russo', region: 'Banlieue', rating: 4.3, deliveries: 98, revenue: 2140 },
        { id: 'd5', name: 'Emma Laurent', region: 'Paris', rating: 4.7, deliveries: 134, revenue: 2980 },
    ];

    // Sort drivers by revenue
    drivers.sort((a, b) => b.revenue - a.revenue);
}

// Update statistics
function updateStats() {
    const totalOrders = orders.length;
    const activeDrivers = drivers.filter(d => d.deliveries > 0).length;
    const pendingOrders = orders.filter(o => o.status === 'pending').length;
    const totalRevenue = orders.reduce((sum, o) => sum + o.amount, 0);

    animateValue('total-orders', 0, totalOrders, 1000);
    animateValue('active-drivers', 0, activeDrivers, 1000);
    animateValue('pending-orders', 0, pendingOrders, 1000);
    animateValue('total-revenue', 0, totalRevenue, 1000, '€');
}

// Animate counter
function animateValue(id, start, end, duration, suffix = '') {
    const element = document.getElementById(id);
    const range = end - start;
    const increment = range / (duration / 16);
    let current = start;

    const timer = setInterval(() => {
        current += increment;
        if (current >= end) {
            current = end;
            clearInterval(timer);
        }
        element.textContent = Math.floor(current) + suffix;
    }, 16);
}

// Render orders list
function renderOrders() {
    const ordersList = document.getElementById('orders-list');
    ordersList.innerHTML = '';

    orders.forEach(order => {
        const orderItem = document.createElement('div');
        orderItem.className = 'order-item';
        orderItem.innerHTML = `
            <span class="order-status ${order.status}"></span>
            <div class="order-info">
                <div class="order-id">${order.id} - ${order.client}</div>
                <div class="order-details">
                    📍 ${order.destination} • ${order.time}
                    ${order.driver ? ` • Livreur: ${order.driver}` : ''}
                </div>
            </div>
            <div class="order-amount">${order.amount}€</div>
        `;
        
        orderItem.addEventListener('click', () => showOrderDetails(order));
        ordersList.appendChild(orderItem);
    });
}

// Render drivers list
function renderDrivers() {
    const driversList = document.getElementById('drivers-list');
    driversList.innerHTML = '';

    drivers.slice(0, 5).forEach((driver, index) => {
        const driverItem = document.createElement('div');
        driverItem.className = 'driver-item';
        
        const initials = driver.name.split(' ').map(n => n[0]).join('');
        
        driverItem.innerHTML = `
            <div class="driver-rank">${index + 1}</div>
            <div class="driver-avatar">${initials}</div>
            <div class="driver-info">
                <div class="driver-name">${driver.name}</div>
                <div class="driver-stats">
                    ${driver.deliveries} livraisons • ${driver.region}
                </div>
            </div>
            <div class="driver-rating">
                ⭐ ${driver.rating}
            </div>
        `;
        
        driversList.appendChild(driverItem);
    });
}

// Refresh orders
function refreshOrders() {
    const btn = event.target.closest('.btn-icon');
    btn.style.transform = 'rotate(360deg)';
    
    setTimeout(() => {
        // Simulate new data
        const newOrder = {
            id: `c${orders.length + 1}`,
            client: `Client ${String.fromCharCode(65 + orders.length)}`,
            destination: ['Marais', 'Belleville', 'Bercy', 'Auteuil'][Math.floor(Math.random() * 4)],
            amount: Math.floor(Math.random() * 30) + 10,
            status: 'pending',
            time: new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })
        };
        
        orders.unshift(newOrder);
        renderOrders();
        updateStats();
        
        btn.style.transform = '';
        
        // Show notification
        showNotification('Nouvelle commande reçue!', 'success');
    }, 500);
}

// Show order details
function showOrderDetails(order) {
    const statusText = {
        'pending': 'En attente',
        'assigned': 'Assignée',
        'delivered': 'Livrée'
    };
    
    alert(`
Commande: ${order.id}
Client: ${order.client}
Destination: ${order.destination}
Montant: ${order.amount}€
Statut: ${statusText[order.status]}
Heure: ${order.time}
${order.driver ? `Livreur: ${order.driver}` : ''}
    `.trim());
}

// Show new order modal
function showNewOrderModal() {
    const client = prompt('Nom du client:');
    if (!client) return;
    
    const destination = prompt('Destination:');
    if (!destination) return;
    
    const amount = prompt('Montant (€):');
    if (!amount) return;
    
    const newOrder = {
        id: `c${orders.length + 1}`,
        client: client,
        destination: destination,
        amount: parseInt(amount),
        status: 'pending',
        time: new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })
    };
    
    orders.unshift(newOrder);
    renderOrders();
    updateStats();
    showNotification('Commande créée avec succès!', 'success');
}

// Show notification
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 80px;
        right: 20px;
        padding: 1rem 1.5rem;
        background: ${type === 'success' ? '#10b981' : '#3b82f6'};
        color: white;
        border-radius: 12px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
        z-index: 1000;
        animation: slideIn 0.3s ease;
    `;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Start real-time updates
function startRealTimeUpdates() {
    setInterval(() => {
        // Simulate status changes
        const pendingOrders = orders.filter(o => o.status === 'pending');
        if (pendingOrders.length > 0 && Math.random() > 0.7) {
            const order = pendingOrders[0];
            order.status = 'assigned';
            order.driver = drivers[Math.floor(Math.random() * drivers.length)].id;
            renderOrders();
            updateStats();
        }
        
        // Simulate deliveries
        const assignedOrders = orders.filter(o => o.status === 'assigned');
        if (assignedOrders.length > 0 && Math.random() > 0.8) {
            const order = assignedOrders[0];
            order.status = 'delivered';
            renderOrders();
            updateStats();
        }
    }, 5000);
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
