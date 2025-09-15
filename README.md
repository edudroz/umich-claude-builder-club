# Claude Builder Club @ Johns Hopkins University

A modern, terminal-style React site for the Johns Hopkins University Claude Builder Club. The UI emulates a command-line interface where visitors can explore the club via typed commands (e.g., `help`, `about`, `join`).

## 🚀 Features

- **Interactive Terminal UI**: Type commands to discover content
- **Boot Screen Animation**: Simulated startup before the terminal loads
- **Command Set**: `help`, `about`, `join`, `events`, `projects`, `contact`, `whoami`, `clear`
- **Branding**: Claude colors, Inter font, and Claude iconography
- **Responsive & Fast**: Works on all devices; optimized front-end

## 💻 Commands Overview

- **help**: List all available commands
- **about**: Mission and what the club offers
- **join**: Application, community links, and membership benefits
- **events**: Highlights and regular sessions
- **projects**: What members are building and how to contribute
- **contact**: Ways to reach leadership and social links
- **whoami**: Session info inside the terminal
- **clear**: Clear the terminal output

## 🎨 Design Elements

### Claude Branding
- **Primary**: Claude Orange (#DA7756)
- **Orange (light/dark)**: #E89980 / #C15F3C
- **Text (primary/secondary/muted)**: #2C2B29 / #6B6B6B / #9B9B9B
- **Surface**: #FFFFFF
- **Status**: Success #059669, Error #DC2626, Warning #D97706
- **Typography**: Inter font family
- **Visual Elements**: Terminal window chrome, scanline effect, typewriter output

## 🛠️ Technical Stack

- **React 18** with hooks and functional components
- **Create React App** setup
- **CSS3** (custom properties, Flexbox/Grid)
- **JavaScript ES6+**
- **Font Awesome** (icons) and **Google Fonts** (Inter)

## 📱 Responsive Design

The site is responsive and optimized for desktop, tablet, and mobile viewports.

## 🚀 Getting Started

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Start the development server**:
   ```bash
   npm start
   ```

3. **Open** [http://localhost:3000](http://localhost:3000) in your browser

4. **Build for production**:
   ```bash
   npm run build
   ```

5. **Deploy** the `build` folder to your preferred hosting service

## 📝 Customization

### Colors and Styles
- Update global colors/variables in `src/App.css` and terminal styling in `src/components/Terminal.css`.
- The terminal chrome, scanlines, prompts, and text colors are defined in `Terminal.css`.

### Commands and Content
- Edit command outputs and behavior in `src/components/Terminal.js` under the `commands` object.
  - Update application link (Join): Google Form URL
  - Update community link: GroupMe
  - Update socials: Instagram and LinkedIn
  - Edit events text, schedule, and workshops
  - Edit leadership names/emails in the `contact` command

### Assets
- Replace or update the Claude logo at `public/claude-logo.svg` if desired.

## 🌐 Deployment

The website can be deployed to any static hosting service:
- **GitHub Pages**: Free hosting for public repositories
- **Netlify**: Drag and drop deployment
- **Vercel**: Fast deployment with custom domains
- **AWS S3**: Scalable cloud hosting

## 📧 Contact

Use the `contact` command on the site for current leadership and links, or reach out via:
- Instagram: `https://www.instagram.com/claude.michigan/`
- LinkedIn: `https://www.linkedin.com/company/claude-builder-club-UMICH/`


## 📄 License

This project is open source and available under the MIT License.

---

**Built with ❤️ for the Johns Hopkins University Claude Builder Club**