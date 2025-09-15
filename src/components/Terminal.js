import React, { useState, useEffect, useRef } from 'react';
import './Terminal.css';

const Terminal = () => {
  const [input, setInput] = useState('');
  const [history, setHistory] = useState([]);
  const [isTyping, setIsTyping] = useState(false);
  const [currentUser] = useState('guest@claude-UMICH');
  const inputRef = useRef(null);
  const terminalRef = useRef(null);

  const commands = {
    help: {
      description: 'Show available commands',
      action: () => [
        '<span class="terminal-header-text">🤖 Welcome to Claude Builder Club @UMICH</span>',
        '',
        '<span class="terminal-subheader">Available Commands:</span>',
        '<span class="terminal-separator">─────────────────────────────────────────────</span>',
        '  <span class="accent-text">about</span>          Learn about our community',
        '  <span class="accent-text">join</span>           How to become a member',
        '  <span class="accent-text">events</span>         Upcoming workshops & events',
        '  <span class="accent-text">projects</span>       What we\'re currently building',
        '  <span class="accent-text">contact</span>        Get in touch with our team',
        '  <span class="accent-text">whoami</span>         Current session info',
        '  <span class="accent-text">clear</span>          Clear the screen',
        '',
        '<span class="success-text">💡 Tip: Just type any command name to explore!</span>',
      ]
    },
    about: {
      description: 'Learn about the club',
      action: () => [
        '<span class="terminal-header-text">🤖 About Claude Builder Club @UMICH</span>',
        '<span class="terminal-separator">═══════════════════════════════════════════</span>',
        '',
        'We\'re a <span class="accent-text">student-led community</span> of builders, creators, and AI enthusiasts working together to shape the future with artificial intelligence.',
        '',
        '<div class="terminal-card"><span class="terminal-subheader">🎯 What We\'re About:</span><br><br>   ▶ <span class="success-text">Hands-on workshops</span> teaching real AI skills<br>   ▶ Building projects that <span class="accent-text">actually help UMICH students</span><br>   ▶ Learning from each other through <span class="highlight-text">collaboration</span><br>   ▶ Getting access to <span class="terminal-badge">Claude Pro</span> and cutting-edge AI tools</div>',
        '',
        '<span class="terminal-subheader">🌟 Our Mission:</span>',
        '<span class="muted-text">Claude Builder Clubs are inclusive communities for all students interested in exploring AI development, developing technical skills, and learning about the benefits and risks associated with AI. CBCs are a space for passionate students to build their own projects while connecting with peers who can elevate their ideas. CBC members are AI thought leaders on their campuses and beyond.</span>',
        '',
        '<span class="success-text">✨ Ready to join the revolution? Try the "join" command!</span>',
      ]
    },
    join: {
      description: 'How to join the community',
      action: () => [
        '<span class="terminal-header-text">🚀 Join the Claude Builder Club Family!</span>',
        '<span class="terminal-separator">═══════════════════════════════════════════</span>',
        '',
        'Ready to dive into the world of <span class="accent-text">AI building</span>? Here\'s how to get started:',
        '',
        '<div class="terminal-step"><span class="terminal-subheader">📝 Step 1: Complete Your Application</span><br>Fill out our quick membership form to tell us about yourself:<br>→ <a href="https://forms.gle/ETBUyYZSvSFxQ13d8" target="_blank" class="terminal-link">https://forms.gle/ETBUyYZSvSFxQ13d8</a></div>',
        '<div class="terminal-step"><span class="terminal-subheader">💬 Step 2: Join Our Community Hub</span><br>Connect with fellow builders on GroupMe:<br>→ <a href="https://groupme.com/join_group/110064927/rSA2fFW6" target="_blank" class="terminal-link">https://groupme.com/join_group/110064927/rSA2fFW6</a></div>',
        '<div class="terminal-step"><span class="terminal-subheader">🏗️ Step 3: Attend Weekly Meetings</span><br>Jump into our weekly hands-on sessions:<br>• <span class="success-text">Time: TBD</span> @ TBD</div>',
        '<div class="terminal-step"><span class="terminal-subheader">📱 Step 4: Stay Connected</span><br>Follow us for updates and inspiration:<br>• Instagram: <a href="https://www.instagram.com/claudeUMICH/" target="_blank" class="terminal-link">@claudeUMICH</a><br>• LinkedIn: <a href="https://www.linkedin.com/company/claude-builder-club-UMICH/" target="_blank" class="terminal-link">Claude Builder Club @ UMICH</a></div>',
        '',
        '<div class="terminal-card"><span class="terminal-subheader">🎁 What You\'ll Get as a Member:</span><br><br>   ✓ <span class="terminal-badge">Free Claude Pro </span> access for your projects<br>   ✓ <span class="terminal-badge">$50</span> in Claude API credits<br>   ✓ <span class="highlight-text">Exclusive workshops</span> with industry experts<br>   ✓ Collaboration on <span class="success-text">real-world projects</span><br>   ✓ Direct networking with <span class="accent-text">AI professionals</span><br>   ✓ A supportive community of like-minded builders</div>',
        '',
        '<span class="muted-text">Questions? Just type "contact" to reach out to our team!</span>',
      ]
    }, // https://www.instagram.com/claudebuilders_UMICH // https://www.linkedin.com/company/claude-builder-club-UMICH/
    events: {
      description: 'Upcoming events and workshops',
      action: () => [
        '<span class="terminal-header-text">📅 Events & Workshops at Claude Builder Club</span>',
        '<span class="terminal-separator">═════════════════════════════════════════════</span>',
        '',
        'Stay ahead of the <span class="accent-text">AI curve</span> with our exciting lineup of events!',
        '',
        '<div class="terminal-step"><span class="terminal-subheader">🔥 This Week\'s Highlights</span><br>Don\'t miss these amazing upcoming events:<br>• <span class="success-text">Claude Tabling:</span>  Tuesday, September 16, 10am EST (In front of Brody)<br>• <span class="success-text">Claude Mini Demo:</span> Wednesday, September 17, 7pm EST (Malone 107)<br></div>',
        // <br>• <span class="success-text">Date: </span> "Event Name"<br>  Event Description
        
        '',
        '<div class="terminal-step"><span class="terminal-subheader">🗓️ Regular Weekly Sessions</span><br>Join us for our consistent building sessions:<br>• <span class="highlight-text">Weekly Meetings:</span> TBD<br>  Learn more about Claude at UMICH</div>',
        '',
        '<div class="terminal-step"><span class="terminal-subheader">🎯 Upcoming Workshop Series</span><br>Deep dive into specialized AI topics:<br>▶ <span class="accent-text">Societal Impacts of AI (Tuesday, September 23, 12pm PST)</span><br>▶ <span class="accent-text">Claude Code (Wednesday, September 24, 4pm PST</span><br>▶ <span class="accent-text">AI Research Salon (Tuesday, September 30, 1pm PST)</span><br>▶ <span class="accent-text">Building Agents (Wednesday, October 1, 4pm PST)</span></div>',
        
        /* <br>▶ <span class="accent-text">Claude Code (Tuesday, October 7, 12pm PST)</span><br>▶ <span class="accent-text">Societal Impacts of AI (Tuesday, October 8, 4pm PST)</span><br>▶ <span class="accent-text">Building Agents (Wednesday, October 21, 12pm PST)</span><br>▶ <span class="accent-text">AI Research Salon (Wednesday, October 22, 4pm PST)</span><br>▶ <span class="accent-text">Building with MCP (Tuesday, October 28, 12pm PST)</span><br>▶ <span class="accent-text">Building with MCP (Wednesday, October 29, 4pm PST)</span><br>▶ <span class="accent-text">Entering the workfoce in a post AI world (Wednesday, November 5, 4pm PST)</span><br>▶ <span class="accent-text">Claude Code (Wednesday, November 12, 4pm PST</span>
        */

        '',
        '<div class="terminal-card"><span class="terminal-subheader">💰 Best Part: All events are completely FREE for members!</span><br><br>   ✓ <span class="terminal-badge">No cost</span> to attend any workshop<br>   ✓ <span class="terminal-badge">Free materials</span> and resources provided<br>   ✓ <span class="terminal-badge">Expert guidance</span> from industry professionals<br>   ✓ <span class="terminal-badge">Networking opportunities</span> with fellow builders</div>',
        '',
        '<div class="terminal-step"><span class="terminal-subheader">📝 How to Join Events</span><br>Ready to participate? Here\'s how:<br>→ <span class="terminal-link">RSVP in our Discord server</span><br>→ <span class="terminal-link">Email us at events@UMICH-claude.org</span><br>→ Check our social media for last-minute updates</div>',
        '',
        '<span class="muted-text">Questions about events? Type "contact" to reach our team!</span>',
      ]
    },
    projects: {
      description: 'Current and past projects',
      action: () => [
        '<span class="terminal-header-text">🚀 Projects We\'re Building at Claude Builder Club</span>',
        '<span class="terminal-separator">═══════════════════════════════════════════════</span>',
        '',
        'From <span class="accent-text">idea to impact</span> - here\'s what our community is creating:',
        '',
        '<div class="terminal-step"><span class="terminal-subheader">⚡ Currently in Development</div>',
        
        /*
        </span><br>Active projects our members are working on:<br>• <span class="highlight-text">🎓 Project Name</span><br>  Project Description</div>',
        '',
        /*
        '<div class="terminal-card"><span class="terminal-subheader">🏆 Recently Launched & Live</span><br><br>   🍽️ <span class="terminal-badge">Project Name</span> (Number active users)<br>      Project Description</div>',
        '',
        */
        /*
        '<div class="terminal-step"><span class="terminal-subheader">🔍 Seeking Contributors</span><br>Join these exciting projects in development:<br>• <span class="success-text">💝 Project Name</span><br>  Project Description</div>',
        */
        '',
        '<div class="terminal-card"><span class="terminal-subheader">💡 Got an idea for a project? We\'d love to hear it!</span><br><br>   ✓ <span class="terminal-badge">Pitch your idea</span> at our weekly meetings<br>   ✓ <span class="terminal-badge">Get feedback</span> from experienced developers<br>   ✓ <span class="terminal-badge">Find collaborators</span> who share your vision<br>   ✓ <span class="terminal-badge">Access resources</span> to bring your project to life</div>',
        '',
        '<span class="muted-text">Ready to start building? Type "join" to become part of our builder community!</span>',
      ]
    },
    contact: {
      description: 'Get in touch',
      action: () => [
        '<span class="terminal-header-text">📬 Get in Touch with Claude Builder Club</span>',
        '<span class="terminal-separator">═══════════════════════════════════════════</span>',
        '',
        'Have questions, ideas, or just want to chat about <span class="accent-text">AI</span>? We\'d love to hear from you!',
        '',
        '<div class="terminal-step"><span class="terminal-subheader">💌 Contact Methods</span><br>Reach out to us through any of these channels:<br>• <span class="highlight-text">💬 GroupMe:</span> <a href="https://groupme.com/join_group/110064927/rSA2fFW6" target="_blank" class="terminal-link">https://groupme.com/join_group/110064927/rSA2fFW6</a><br>  Join our active community for real-time chat<br>• <span class="highlight-text">📱 Instagram:</span> <a href="https://www.instagram.com/claudeUMICH/" target="_blank" class="terminal-link">@claudeUMICH</a><br>  Follow for behind-the-scenes content and updates<br>• <span class="highlight-text">💼 LinkedIn:</span> <a href="https://www.linkedin.com/company/claude-builder-club-UMICH/" target="_blank" class="terminal-link">https://www.linkedin.com/company/claude-builder-club-UMICH/</a><br>  Connect professionally and see our latest achievements</div>',
        '', 
        '<div class="terminal-step"><span class="terminal-subheader">🏢 Visit Us in Person</span><br>Come hang out with us on campus:<br>• <span class="success-text">📍 Weekly Meetings:</span> TBD<br>• <span class="success-text">🕐 When:</span> TBD<br>• <span class="success-text">☕ Bring your laptop</span> and grab some coffee with us!</div>',
        '',
        '<div class="terminal-card"><span class="terminal-subheader">👥 Meet Our Leadership Team</span><br><br>   🌟 <span class="terminal-badge">Nathan Baek</span> - Claude Builder Ambassador<br>      📧 <span class="terminal-link">sbaek19@UMICH.edu</span><br>   🌟 <span class="terminal-badge">Sahana Sanjeev</span> - Claude Builder Ambassador<br>      📧 <span class="terminal-link">ssanjee3@UMICH.edu</span><br>   🌟 <span class="terminal-badge">Amelia Frank</span> - Claude Campus Ambassador<br>      📧 <span class="terminal-link">afrank33@UMICH.edu</span></div>',
        '',
        '<div class="terminal-step"><span class="terminal-subheader">💭 Ready to Get Started?</span><br>Whether you\'re a complete beginner or an AI expert,<br>we\'re here to help you <span class="highlight-text">build something amazing</span>!<br><br>→ Type <span class="accent-text">"join"</span> to become a member<br>→ Type <span class="accent-text">"events"</span> to see what\'s happening<br>→ Type <span class="accent-text">"projects"</span> to explore our work</div>',
      ]
    },
    clear: {
      description: 'Clear the terminal',
      action: () => 'CLEAR'
    },
    whoami: {
      description: 'Display current user',
      action: () => [
        '👤 Current Session Information',
        '═══════════════════════════════════════════',
        '',
        `🔐 User: ${currentUser}`,
        '🖥️  Terminal: Claude Builder Club @UMICH Interactive Portal',
        '📅 Session: ' + new Date().toLocaleDateString(),
        '🕒 Time: ' + new Date().toLocaleTimeString(),
        '',
        '🎯 Access Level: Guest Explorer',
        '   You\'re currently browsing as a visitor.',
        '   Ready to become a full member? Type "join" to get started!',
        '',
        '🌟 Available Commands: Type "help" to see what you can explore',
        '💡 Pro Tip: Each command reveals more about our amazing community!',
      ]
    }
  };

  const typeMessage = async (lines, delay = 15) => {
    setIsTyping(true);
    
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      
      // Add new line to history for this line
      setHistory(prev => [...prev, { type: 'output', content: '' }]);
      
      await new Promise(resolve => {
        let index = 0;
        const typing = setInterval(() => {
          if (index <= line.length) {
            setHistory(prev => {
              const newHistory = [...prev];
              newHistory[newHistory.length - 1] = {
                type: 'output',
                content: line.substring(0, index)
              };
              return newHistory;
            });
            index++;
          } else {
            clearInterval(typing);
            resolve();
          }
        }, delay);
      });
      
      // Add small delay between lines
      if (i < lines.length - 1) {
        await new Promise(resolve => setTimeout(resolve, 30));
      }
    }
    
    setIsTyping(false);
  };

  useEffect(() => {
    // Welcome message
    typeMessage([
      '<span class="terminal-header-text">🤖 Welcome to Claude Builder Club @UMICH</span>',
      '<span class="terminal-separator">═══════════════════════════════════════════</span>',
      '<span class="muted-text">University of Michigan  AI Community</span>',
      '<span class="success-text">🚀 Ready to explore the future of AI building?</span>',
      '<div class="terminal-card"><span class="terminal-subheader">💡 Quick Start:</span><br><br>   → Type <span class="accent-text">"help"</span> to see all available commands<br>   → Type <span class="accent-text">"about"</span> to learn about our community<br>   → Type <span class="accent-text">"join"</span> if you\'re ready to become a builder</div>',
      '<span class="highlight-text">Let\'s build something amazing together! ✨</span>',
    ], 15);

    // Focus input
    inputRef.current?.focus();
  }, []);

  const executeCommand = async (cmd) => {
    const trimmedCmd = cmd.trim().toLowerCase();
    
    // Add command to history
    setHistory(prev => [...prev, { 
      type: 'command', 
      content: `${currentUser}:~$ ${cmd}`,
      timestamp: new Date()
    }]);

    // Execute command
    if (commands[trimmedCmd]) {
      const result = commands[trimmedCmd].action();
      
      if (result === 'CLEAR') {
        setHistory([]);
        return;
      }
      
      // Add empty line for output
      setHistory(prev => [...prev, { type: 'output', content: '' }]);
      
      // Type out response
      await typeMessage(Array.isArray(result) ? result : [result]);
    } else if (trimmedCmd === '') {
      // Empty command
      return;
    } else {
      // Unknown command
      setHistory(prev => [...prev, { 
        type: 'error', 
        content: `bash: ${trimmedCmd}: command not found\nType "help" for available commands.`
      }]);
    }

    // Add spacing
    setHistory(prev => [...prev, { type: 'output', content: '' }]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (input.trim() && !isTyping) {
      await executeCommand(input);
      setInput('');
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Tab') {
      e.preventDefault();
      // Simple tab completion
      const cmdStart = input.toLowerCase();
      const matches = Object.keys(commands).filter(cmd => cmd.startsWith(cmdStart));
      if (matches.length === 1) {
        setInput(matches[0]);
      }
    }
  };

  useEffect(() => {
    // Auto-scroll to bottom
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [history]);

  return (
    <div className="terminal-container">
      <div className="scanlines"></div>
      <div className="terminal-window">
        <div className="terminal-header">
          <div className="terminal-controls">
            <div className="control-btn close"></div>
            <div className="control-btn minimize"></div>
            <div className="control-btn maximize"></div>
          </div>
          <div className="terminal-title">
            <img src="/claude-logo.svg" alt="Claude" className="terminal-logo" />
            claude@UMICH-builder-club ~ Terminal
          </div>
        </div>
        
        <div className="terminal-body" ref={terminalRef}>
          {history.map((entry, index) => (
            <div key={index} className={`terminal-line ${entry.type}`}>
              <span dangerouslySetInnerHTML={{ __html: entry.content }} />
            </div>
          ))}
          
          {!isTyping && (
            <form onSubmit={handleSubmit} className="terminal-input-line">
              <span className="terminal-prompt">{currentUser}:~$ </span>
              <div className="input-container">
                <span className="input-display">{input}</span>
                <input
                  ref={inputRef}
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={handleKeyDown}
                  className="terminal-input-hidden"
                  autoComplete="off"
                  autoFocus
                />
                <span className="cursor">█</span>
              </div>
            </form>
          )}
          
          {isTyping && (
            <div className="terminal-line">
              <span className="cursor typing-cursor">█</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Terminal;