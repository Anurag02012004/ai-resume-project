'use client';

import { useState, useEffect } from 'react';
import { 
  User, 
  Briefcase, 
  Code, 
  MessageCircle, 
  Send, 
  Loader2, 
  ExternalLink,
  Calendar,
  MapPin,
  Award,
  GitBranch
} from 'lucide-react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function Home() {
  const [activeTab, setActiveTab] = useState('profile');
  const [profileData, setProfileData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // Chat state
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);

  // Fetch profile data on mount
  useEffect(() => {
    if (activeTab === 'profile') {
      fetchProfileData();
    }
  }, [activeTab]);

  const fetchProfileData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_URL}/api/v1/profile`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setProfileData(data);
    } catch (err) {
      setError(`Failed to load profile data: ${err.message}`);
      console.error('Error fetching profile:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    
    if (!inputValue.trim()) return;
    
    const userMessage = inputValue.trim();
    setInputValue('');
    
    // Add user message to chat
    setMessages(prev => [...prev, { type: 'user', content: userMessage }]);
    setIsTyping(true);
    
    try {
      const response = await fetch(`${API_URL}/api/v1/query-resume`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: userMessage }),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      // Add AI response to chat
      setMessages(prev => [...prev, { 
        type: 'ai', 
        content: data.answer,
        sources: data.sources 
      }]);
      
    } catch (err) {
      setMessages(prev => [...prev, { 
        type: 'ai', 
        content: `I apologize, but I encountered an error while processing your question: ${err.message}. Please try again.` 
      }]);
    } finally {
      setIsTyping(false);
    }
  };

  const renderProfileTab = () => {
    if (loading) {
      return (
        <div className="flex items-center justify-center h-64">
          <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
          <span className="ml-2 text-gray-600">Loading profile data...</span>
        </div>
      );
    }

    if (error) {
      return (
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
          <p className="text-red-600 mb-4">{error}</p>
          <button 
            onClick={fetchProfileData}
            className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors"
          >
            Retry
          </button>
        </div>
      );
    }

    if (!profileData) {
      return (
        <div className="text-center py-12">
          <p className="text-gray-600">No profile data available</p>
        </div>
      );
    }

    return (
      <div className="space-y-8 animate-fade-in">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl p-8">
          <div className="flex items-center space-x-4">
            <div className="bg-white/20 p-3 rounded-full">
              <User className="w-8 h-8" />
            </div>
            <div>
              <h1 className="text-3xl font-bold">AI-Powered Resume</h1>
              <p className="text-blue-100 mt-1">Full Stack Engineer & AI Specialist</p>
            </div>
          </div>
        </div>

        {/* Experience Section */}
        <section>
          <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center">
            <Briefcase className="w-6 h-6 mr-2 text-blue-600" />
            Work Experience
          </h2>
          <div className="space-y-6">
            {profileData.experiences.map((exp) => (
              <div key={exp.id} className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm hover:shadow-md transition-shadow">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="text-xl font-semibold text-gray-800">{exp.role}</h3>
                    <p className="text-blue-600 font-medium">{exp.company}</p>
                  </div>
                  <div className="flex items-center text-gray-500 text-sm">
                    <Calendar className="w-4 h-4 mr-1" />
                    {exp.start_date} - {exp.end_date || 'Present'}
                  </div>
                </div>
                <ul className="space-y-2">
                  {exp.description.map((desc, index) => (
                    <li key={index} className="text-gray-700 flex items-start">
                      <span className="w-2 h-2 bg-blue-600 rounded-full mt-2 mr-3 flex-shrink-0"></span>
                      {desc}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </section>

        {/* Projects Section */}
        <section>
          <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center">
            <Code className="w-6 h-6 mr-2 text-blue-600" />
            Featured Projects
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {profileData.projects.map((project) => (
              <div key={project.id} className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm hover:shadow-lg transition-all duration-300">
                <div className="flex justify-between items-start mb-4">
                  <h3 className="text-lg font-semibold text-gray-800">{project.title}</h3>
                  {project.repo_url && (
                    <a 
                      href={project.repo_url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-gray-400 hover:text-blue-600 transition-colors"
                    >
                      <ExternalLink className="w-5 h-5" />
                    </a>
                  )}
                </div>
                <p className="text-gray-700 mb-4 leading-relaxed">{project.description}</p>
                <div className="flex flex-wrap gap-2">
                  {project.tech_stack.map((tech) => (
                    <span 
                      key={tech} 
                      className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium"
                    >
                      {tech}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Skills Section */}
        <section>
          <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center">
            <Award className="w-6 h-6 mr-2 text-blue-600" />
            Technical Skills
          </h2>
          <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
            {(() => {
              const skillsByCategory = profileData.skills.reduce((acc, skill) => {
                if (!acc[skill.category]) {
                  acc[skill.category] = [];
                }
                acc[skill.category].push(skill.name);
                return acc;
              }, {});

              return Object.entries(skillsByCategory).map(([category, skills]) => (
                <div key={category} className="mb-6 last:mb-0">
                  <h3 className="text-lg font-semibold text-gray-800 mb-3">{category}</h3>
                  <div className="flex flex-wrap gap-2">
                    {skills.map((skill) => (
                      <span 
                        key={skill} 
                        className="bg-gray-100 text-gray-700 px-3 py-1 rounded-lg text-sm font-medium hover:bg-gray-200 transition-colors"
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              ));
            })()}
          </div>
        </section>

        {/* Education Section */}
        <section>
          <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center">
            <Award className="w-6 h-6 mr-2 text-blue-600" />
            Education
          </h2>
          <div className="space-y-4">
            {profileData.education && profileData.education.map((edu) => (
              <div key={edu.id} className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm hover:shadow-md transition-shadow">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="text-xl font-semibold text-gray-800">{edu.degree}</h3>
                    <p className="text-blue-600 font-medium">{edu.institution}</p>
                    <p className="text-gray-500 text-sm flex items-center mt-1">
                      <MapPin className="w-4 h-4 mr-1" />
                      {edu.location}
                    </p>
                  </div>
                  <div className="flex items-center text-gray-500 text-sm">
                    <Calendar className="w-4 h-4 mr-1" />
                    {edu.start_date} - {edu.end_date || 'Present'}
                  </div>
                </div>
                <ul className="space-y-2">
                  {edu.description.map((desc, index) => (
                    <li key={index} className="text-gray-700 flex items-start">
                      <span className="w-2 h-2 bg-blue-600 rounded-full mt-2 mr-3 flex-shrink-0"></span>
                      {desc}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </section>

        {/* Certificates Section */}
        <section>
          <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center">
            <Award className="w-6 h-6 mr-2 text-green-600" />
            Certificates
          </h2>
          <div className="grid md:grid-cols-2 gap-6">
            {profileData.certificates && profileData.certificates.map((cert) => (
              <div key={cert.id} className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm hover:shadow-md transition-shadow">
                <div className="flex justify-between items-start mb-4">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-800 mb-2">{cert.title}</h3>
                    <p className="text-green-600 font-medium mb-1">{cert.issuer}</p>
                    <p className="text-gray-500 text-sm flex items-center">
                      <Calendar className="w-4 h-4 mr-1" />
                      {cert.issue_date}
                    </p>
                  </div>
                  {cert.credential_url && (
                    <a
                      href={cert.credential_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="bg-green-600 text-white px-3 py-2 rounded-lg hover:bg-green-700 transition-colors flex items-center space-x-2 text-sm"
                    >
                      <span>View</span>
                      <ExternalLink className="w-4 h-4" />
                    </a>
                  )}
                </div>
                {cert.description && (
                  <p className="text-gray-700 text-sm">{cert.description}</p>
                )}
              </div>
            ))}
          </div>
        </section>
      </div>
    );
  };

  const renderChatTab = () => {
    return (
      <div className="h-full flex flex-col animate-fade-in">
        {/* Chat Header */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6 rounded-t-xl">
          <div className="flex items-center space-x-3">
            <div className="bg-white/20 p-2 rounded-full">
              <MessageCircle className="w-6 h-6" />
            </div>
            <div>
              <h2 className="text-xl font-bold">AI Resume Assistant</h2>
              <p className="text-blue-100 text-sm">Ask me anything about my experience, projects, or skills!</p>
            </div>
          </div>
        </div>

        {/* Chat Messages */}
        <div className="flex-1 overflow-y-auto p-6 bg-gray-50 space-y-4" style={{ minHeight: '400px', maxHeight: '600px' }}>
          {messages.length === 0 && (
            <div className="text-center py-12">
              <MessageCircle className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600 mb-2">Start a conversation!</p>
              <p className="text-gray-500 text-sm">Ask me about my work experience, projects, or technical skills.</p>
              <div className="mt-6 flex flex-wrap gap-2 justify-center">
                <button 
                  onClick={() => setInputValue("What programming languages do you know?")}
                  className="bg-white border border-gray-200 px-3 py-2 rounded-lg text-sm hover:bg-gray-50 transition-colors"
                >
                  What programming languages do you know?
                </button>
                <button 
                  onClick={() => setInputValue("Tell me about your recent projects")}
                  className="bg-white border border-gray-200 px-3 py-2 rounded-lg text-sm hover:bg-gray-50 transition-colors"
                >
                  Tell me about your recent projects
                </button>
                <button 
                  onClick={() => setInputValue("What is your work experience?")}
                  className="bg-white border border-gray-200 px-3 py-2 rounded-lg text-sm hover:bg-gray-50 transition-colors"
                >
                  What is your work experience?
                </button>
              </div>
            </div>
          )}

          {messages.map((message, index) => (
            <div key={index} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-3xl p-4 rounded-lg ${
                message.type === 'user' 
                  ? 'bg-blue-600 text-white font-medium' 
                  : 'bg-white border border-gray-200 shadow-sm text-gray-900'
              }`}>
                <div className="whitespace-pre-wrap leading-relaxed font-medium">{message.content}</div>
                {message.sources && message.sources.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-gray-200">
                    <p className="text-xs text-gray-700 mb-2 font-semibold">Sources:</p>
                    <div className="space-y-1">
                      {message.sources.map((source, sourceIndex) => (
                        <div key={sourceIndex} className="text-xs bg-blue-50 border border-blue-200 p-2 rounded">
                          <span className="font-semibold text-blue-800">{source.title}</span>
                          <span className="text-blue-600 ml-2">({source.type})</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}

          {isTyping && (
            <div className="flex justify-start">
              <div className="bg-white border border-gray-200 shadow-sm p-4 rounded-lg">
                <div className="loading-dots">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
                <span className="ml-2 text-gray-700 text-sm font-medium">AI is thinking...</span>
              </div>
            </div>
          )}
        </div>

        {/* Chat Input */}
        <div className="bg-white border-t border-gray-200 p-4 rounded-b-xl">
          <form onSubmit={handleSendMessage} className="flex space-x-4">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Ask me about my experience, projects, or skills..."
              className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              disabled={isTyping}
            />
            <button
              type="submit"
              disabled={!inputValue.trim() || isTyping}
              className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center"
            >
              {isTyping ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Send className="w-4 h-4" />
              )}
            </button>
          </form>
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="max-w-6xl mx-auto px-4 py-8">
        {/* Tab Navigation */}
        <div className="bg-white rounded-lg shadow-sm mb-8">
          <div className="flex border-b border-gray-200">
            <button
              onClick={() => setActiveTab('profile')}
              className={`flex-1 py-4 px-6 text-center font-medium transition-colors ${
                activeTab === 'profile'
                  ? 'text-blue-600 border-b-2 border-blue-600 bg-blue-50'
                  : 'text-gray-600 hover:text-gray-800 hover:bg-gray-50'
              }`}
            >
              <User className="w-5 h-5 inline mr-2" />
              My Profile
            </button>
            <button
              onClick={() => setActiveTab('chat')}
              className={`flex-1 py-4 px-6 text-center font-medium transition-colors ${
                activeTab === 'chat'
                  ? 'text-blue-600 border-b-2 border-blue-600 bg-blue-50'
                  : 'text-gray-600 hover:text-gray-800 hover:bg-gray-50'
              }`}
            >
              <MessageCircle className="w-5 h-5 inline mr-2" />
              AI Chat Assistant
            </button>
          </div>
        </div>

        {/* Tab Content */}
        <div className="bg-white rounded-lg shadow-sm overflow-hidden">
          {activeTab === 'profile' ? renderProfileTab() : renderChatTab()}
        </div>
      </div>
    </div>
  );
}
