
import React from 'react';

export const Footer = () => {
    return (
        <footer className="bg-white pt-20 pb-10 border-t border-gray-100">
            <div className="max-w-7xl mx-auto px-4">
                <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-12 mb-16">
                    <div className="col-span-2 lg:col-span-2">
                        <div className="flex items-center gap-2 mb-6">
                            <div className="w-8 h-8 bg-gradient-to-br from-teal-400 to-blue-500 rounded-lg flex items-center justify-center">
                                <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                                </svg>
                            </div>
                            <span className="text-xl font-bold tracking-tight text-slate-900">InfiniteBZ</span>
                        </div>
                        <p className="text-slate-500 max-w-sm mb-8">
                            Building the most connected business community in the world, starting with the vibrant tech hub of Chennai.
                        </p>
                        <div className="flex gap-4">
                            {[1, 2, 3, 4].map(i => (
                                <div key={i} className="w-8 h-8 rounded-full bg-slate-50 flex items-center justify-center text-slate-400 hover:bg-teal-50 hover:text-teal-600 cursor-pointer transition-colors">
                                    <div className="w-4 h-4 bg-current rounded-sm"></div>
                                </div>
                            ))}
                        </div>
                    </div>

                    <FooterColumn title="Platform" links={['Home', 'Platform', 'Private Summit', 'Resources', 'Contact Us']} />
                    <FooterColumn title="Resources" links={['About', 'Research', 'Blogs', 'Terms & Service', 'Privacy Policy']} />
                    <FooterColumn title="Company" links={['Company', 'Blog', 'For Companies', 'Careers']} />
                </div>

                <div className="flex flex-col md:flex-row justify-between items-center pt-8 border-t border-gray-50">
                    <p className="text-slate-400 text-sm">&copy; 2024 InfiniteBZ. All rights reserved.</p>
                    <div className="flex gap-8 mt-4 md:mt-0">
                        <span className="text-slate-400 text-sm hover:text-slate-600 cursor-pointer">Status: 2024</span>
                        <span className="text-slate-400 text-sm hover:text-slate-600 cursor-pointer">Region: Chennai</span>
                    </div>
                </div>
            </div>
        </footer>
    );
};

const FooterColumn = ({ title, links }) => (
    <div className="flex flex-col gap-4">
        <h5 className="font-bold text-slate-800">{title}</h5>
        {links.map(link => (
            <a key={link} href="#" className="text-slate-500 hover:text-teal-600 transition-colors text-sm">{link}</a>
        ))}
    </div>
);
