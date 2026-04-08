import { useState } from 'react';
import { Shield, AlertTriangle, Phone, MapPin, ChevronDown, ChevronUp } from 'lucide-react';
import './SafetyTips.css';

interface AccordionItem {
    id: string;
    title: string;
    icon: any;
    content: string[];
}

export default function SafetyTips() {
    const [openItem, setOpenItem] = useState<string | null>('before');

    const toggleItem = (id: string) => {
        setOpenItem(openItem === id ? null : id);
    };

    const safetyContent: AccordionItem[] = [
        {
            id: 'before',
            title: 'Before a Flood',
            icon: Shield,
            content: [
                'Stay informed about weather forecasts and flood warnings',
                'Prepare an emergency kit with essentials (water, food, medicine, flashlight)',
                'Keep important documents in waterproof containers',
                'Know your evacuation routes and shelter locations',
                'Move valuable items to higher floors',
                'Install check valves in plumbing to prevent backflow',
                'Consider flood insurance for your property',
            ],
        },
        {
            id: 'during',
            title: 'During a Flood',
            icon: AlertTriangle,
            content: [
                'Move to higher ground immediately if flooding begins',
                'Never walk, swim, or drive through flood waters',
                'Stay away from power lines and electrical wires',
                'Listen to emergency broadcasts for updates',
                'If trapped in a building, go to the highest level',
                'Do not touch electrical equipment if wet',
                'Signal for help if needed (whistle, flashlight, bright cloth)',
            ],
        },
        {
            id: 'after',
            title: 'After a Flood',
            icon: MapPin,
            content: [
                'Return home only when authorities say it is safe',
                'Avoid floodwater as it may be contaminated',
                'Document property damage with photos for insurance',
                'Clean and disinfect everything that got wet',
                'Check for structural damage before entering buildings',
                'Throw away food that came in contact with floodwater',
                'Watch for animals, especially snakes',
            ],
        },
    ];

    const emergencyContacts = [
        { name: 'National Emergency', number: '999' },
        { name: 'Fire Service', number: '102' },
        { name: 'Police', number: '100' },
        { name: 'Disaster Management', number: '1090' },
    ];

    const faqs = [
        {
            q: 'What is considered a flood risk area?',
            a: 'Areas near rivers, coastal regions, low-lying lands, and regions with poor drainage are considered high flood risk areas.',
        },
        {
            q: 'How accurate are flood predictions?',
            a: 'Our ML model provides predictions based on historical data, terrain, and weather patterns with confidence scores to help you assess reliability.',
        },
        {
            q: 'When should I evacuate?',
            a: 'Evacuate immediately when local authorities issue evacuation orders, or when you observe rapidly rising water levels.',
        },
        {
            q: 'What should be in my emergency kit?',
            a: 'Include water (1 gallon per person per day), non-perishable food, first aid kit, medications, flashlight, batteries, radio, and important documents.',
        },
    ];

    return (
        <div className="safety-tips-page">
            <div className="safety-header">
                <h1>🛡️ Flood Safety Guide</h1>
                <p>Essential information to keep you and your family safe</p>
            </div>

            {/* Safety Accordion */}
            <div className="safety-accordion">
                {safetyContent.map((item) => {
                    const Icon = item.icon;
                    const isOpen = openItem === item.id;

                    return (
                        <div key={item.id} className={`accordion-item glass ${isOpen ? 'open' : ''}`}>
                            <button
                                className="accordion-header"
                                onClick={() => toggleItem(item.id)}
                            >
                                <div className="accordion-title">
                                    <Icon size={24} />
                                    <h3>{item.title}</h3>
                                </div>
                                {isOpen ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
                            </button>

                            {isOpen && (
                                <div className="accordion-content">
                                    <ul>
                                        {item.content.map((point, idx) => (
                                            <li key={idx}>{point}</li>
                                        ))}
                                    </ul>
                                </div>
                            )}
                        </div>
                    );
                })}
            </div>

            {/* Emergency Contacts */}
            <div className="emergency-contacts glass">
                <h3>
                    <Phone size={24} />
                    Emergency Contacts (Bangladesh)
                </h3>
                <div className="contacts-grid">
                    {emergencyContacts.map((contact) => (
                        <div key={contact.name} className="contact-card">
                            <span className="contact-name">{contact.name}</span>
                            <a href={`tel:${contact.number}`} className="contact-number">
                                {contact.number}
                            </a>
                        </div>
                    ))}
                </div>
            </div>

            {/* FAQ Section */}
            <div className="faq-section glass">
                <h3>❓ Frequently Asked Questions</h3>
                <div className="faq-list">
                    {faqs.map((faq, idx) => (
                        <div key={idx} className="faq-item">
                            <h4>{faq.q}</h4>
                            <p>{faq.a}</p>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
