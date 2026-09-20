import React from 'react';
import { Search, Globe, CheckSquare, AlertTriangle, BookOpen, Gavel, FileText, Image } from 'lucide-react';
import { useLanguage } from '../context/LanguageContext';

const agents = [

  { num: '01', icon: Search, name: 'Claim Extractor', desc: 'Identifies and isolates discrete, verifiable factual assertions from multimodal input. Produces structured claim objects for downstream agents.' },
  { num: '02', icon: Globe, name: 'Evidence Finder', desc: 'Performs RAG over Wikipedia and open web search. Ranks retrieved passages by relevance and passes provenance metadata to the Fact Checker.' },
  { num: '03', icon: CheckSquare, name: 'Fact Checker', desc: 'Compares each claim against retrieved evidence. Produces per-claim verdicts: Supported, Contradicted, or Unverified.' },
  { num: '04', icon: AlertTriangle, name: 'Risk Assessor', desc: 'Integrates forensic signals from text and image analysis tracks with fact-checking results. Produces calibrated fake score, risk level, and confidence.' },
  { num: '05', icon: BookOpen, name: 'Explainability Agent', desc: 'Builds a traceable reasoning chain grounded in the structured outputs of all preceding agents. Produces a human-readable, step-by-step explanation of the verdict.' },
  { num: '06', icon: Gavel, name: 'Final Judge', desc: 'Synthesises all upstream outputs to produce the final verdict, trust score, and confidence rating. Ensures no black-box result.' },
];

const forensicTracks = [
  {
    label: 'Text Forensics',
    icon: FileText,
    tools: [
      { name: 'VADER', desc: 'Valence Aware Dictionary for sEntiment Reasoning — sentence-level sentiment scoring.' },
      { name: 'TextStat', desc: 'Readability metrics including Flesch, Flesch-Kincaid, and Gunning Fog indices.' },
      { name: 'spaCy', desc: 'Named Entity Recognition, Part-of-Speech tagging, and stylistic anomaly detection.' },
    ],
  },
  {
    label: 'Image Forensics',
    icon: Image,
    tools: [
      { name: 'ELA', desc: 'Error Level Analysis — detects inconsistent JPEG compression indicating manipulation.' },
      { name: 'EXIF Metadata', desc: 'Extracts and audits camera metadata, timestamps, and software fingerprints.' },
      { name: 'Noise Pattern Analysis', desc: 'Detects pixel-level noise inconsistencies that indicate image splicing.' },
    ],
  },
];

interface TeamMember {
  name: string;
  role: string;
  photo: string;
  linkedin: string;
  github: string;
}

const teamMembers: TeamMember[] = [
  {
    name: 'Sujal Kumar',
    role: 'Team Lead · Full-Stack/AI Integration',
    photo: '/team/sujal.png',
    linkedin: 'https://www.linkedin.com/in/sujal-kumar-ddu/',
    github: 'https://github.com/Sujal-CSE25',
  },
  {
    name: 'Aayush Mani Tripathi',
    role: 'Backend / AI-ML',
    photo: '/team/aayush.png',
    linkedin: 'https://www.linkedin.com/in/aayush-mani-tripathi-97a767382/',
    github: 'https://github.com/aayushhh1221',
  },
  {
    name: 'Om Narayana',
    role: 'Frontend / UI',
    photo: '/team/om.png',
    linkedin: 'https://www.linkedin.com/in/om-narayana-cse/',
    github: 'https://github.com/Om-CSE25',
  },
  {
    name: 'Ritesh Kumar Gautam',
    role: 'Backend & System Engineering',
    photo: '/team/ritesh.png',
    linkedin: 'https://www.linkedin.com/in/ritesh-gautam-er/',
    github: 'https://github.com/Sujal-CSE25',
  },
  {
    name: 'Anuradha Kushwaha',
    role: 'AI / Research & Documentation',
    photo: '/team/anuradha.png',
    linkedin: 'https://www.linkedin.com/in/anuradha-kushwaha-883892309/',
    github: 'https://github.com/anuradhakushwaha230-ui',
  },
  {
    name: 'Aarushi Raj',
    role: 'Research / Testing & Documentation',
    photo: '/team/aarushi.png',
    linkedin: 'https://www.linkedin.com/in/anuradha-kushwaha-883892309/',
    github: 'https://github.com/aayushhh1221',
  },
];

export const AboutPage: React.FC = () => {
  const { t } = useLanguage();

  return (
    <main id="main-content" tabIndex={-1}>
      <div className="page-header-band">
        <div className="page-header-inner">
          <div className="breadcrumb">
            <a href="/">{t('nav.home')}</a>
            <span className="breadcrumb-sep">/</span>
            <span aria-current="page">{t('nav.about')}</span>
          </div>
          <h1 className="page-header-title">{t('about.title')}</h1>
          <p className="page-header-sub">{t('about.sub')}</p>
        </div>
      </div>

      <section className="section">
        <div className="container">
          <div className="card about-section">
            <h2>{t('about.whatIs')}</h2>

            <p>
              TruthLens AI 3.0 is an AI-Based Fake Identity &amp; Document Screening System
              developed for SIH 2026 (Problem Statement 26188), deployed under the Ministry of Home Affairs
              / Sashastra Seema Bal (SSB). It screens passports and identity documents at borders using
              real AI and forensic signal analysis.
            </p>
            <p>
              The platform integrates a six-agent AI pipeline with dedicated text and image forensic tracks,
              calibrated trust/risk scoring, and an explainability system that traces every verdict back
              to specific evidence and pipeline outputs.
            </p>
            <div style={{ background: 'var(--c-warning-bg)', border: '1px solid #e9d098', borderRadius: 'var(--r-md)', padding: '12px 16px', marginTop: '12px' }}>
              <strong style={{ fontSize: '13px', color: 'var(--c-warning)' }}>⚠ Prototype Notice:</strong>
              <span style={{ fontSize: '13px', color: 'var(--c-warning)', marginLeft: '6px' }}>
                This is a SIH 2026 prototype. It is not an official Government of India service unless
                formally authorised by the appropriate authority.
              </span>
            </div>
          </div>

          {/* Six-Agent Architecture */}
          <div className="about-section" style={{ marginTop: '28px' }}>
            <h2 style={{ fontSize: '20px', fontWeight: 700, color: 'var(--c-navy)', marginBottom: '16px' }}>
              Six-Agent Architecture
            </h2>
            <div className="about-arch-grid">
              {agents.map(({ num, icon: Icon, name, desc }) => (
                <div key={num} className="arch-card">
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
                    <div style={{ width: '32px', height: '32px', background: 'var(--c-light-blue)', borderRadius: 'var(--r-sm)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                      <Icon size={15} color="var(--c-blue)" aria-hidden="true" />
                    </div>
                    <div>
                      <div className="arch-num">Agent {num}</div>
                      <div className="arch-name">{name}</div>
                    </div>
                  </div>
                  <div className="arch-desc">{desc}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Forensic Tracks */}
          <div className="about-section" style={{ marginTop: '28px' }}>
            <h2 style={{ fontSize: '20px', fontWeight: 700, color: 'var(--c-navy)', marginBottom: '16px' }}>
              Forensic Analysis
            </h2>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
              {forensicTracks.map(({ label, icon: Icon, tools }) => (
                <div key={label} className="card">
                  <div className="card-header">
                    <Icon size={15} color="var(--c-blue)" aria-hidden="true" />
                    <div className="card-title">{label}</div>
                  </div>
                  {tools.map(({ name, desc }) => (
                    <div key={name} style={{ padding: '10px 0', borderBottom: '1px solid var(--c-divider)' }}>
                      <div style={{ fontWeight: 700, fontSize: '13px', color: 'var(--c-navy)', marginBottom: '3px' }}>{name}</div>
                      <div style={{ fontSize: '12px', color: 'var(--c-text-secondary)', lineHeight: 1.5 }}>{desc}</div>
                    </div>
                  ))}
                </div>
              ))}
            </div>
          </div>

          {/* Evidence Retrieval */}
          <div className="card about-section" style={{ marginTop: '28px' }}>
            <h2>Evidence Retrieval (RAG)</h2>
            <p>
              The Evidence Finder agent uses Retrieval-Augmented Generation (RAG) to retrieve evidence
              from Wikipedia and open web search. Retrieved passages are ranked by relevance and passed
              with full provenance metadata — including source URL, retrieval timestamp, and claim match —
              to the Fact Checker agent.
            </p>
            <p>
              TruthLens does not hallucinate evidence. All evidence citations are grounded in actual
              retrieved documents.
            </p>
          </div>

          {/* Explainability */}
          <div className="card about-section" style={{ marginTop: '20px' }}>
            <h2>Explainability &amp; Traceability</h2>
            <p>
              Every TruthLens verdict is accompanied by a traceable reasoning chain. The Explainability Agent
              produces a step-by-step account of how the final verdict was reached, grounded in the
              structured outputs of the Claim Extractor, Evidence Finder, Fact Checker, and Risk Assessor.
            </p>
            <p>
              This is a core TruthLens differentiator: every verdict can be inspected stage by stage,
              with claim-level evidence and forensic signal contributions visible to the user.
            </p>
          </div>

          {/* Research */}
          <div className="card about-section" style={{ marginTop: '20px' }}>
            <h2>Research Foundation</h2>
            <p>
              TruthLens AI 3.0 addresses four critical gaps in border identity verification and document screening systems:
            </p>
            <div style={{ marginTop: '12px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {[
                ['Claim-level decomposition', 'Claim Extractor + Fact Checker decompose content into discrete verifiable assertions rather than treating the entire input as one binary verdict.'],
                ['Native forensic integration', 'Text and image forensic tracks feed the Risk Assessor directly, grounding the risk score in real forensic signals.'],
                ['Calibrated trust output', 'The system produces a calibrated fake score, risk level, and final confidence — not a single arbitrary percentage.'],
                ['Explanation traceability', 'A dedicated Explainability Agent produces a structured, step-by-step reasoning chain grounded in pipeline outputs.'],
              ].map(([gap, desc]) => (
                <div key={gap} style={{ background: 'var(--c-surface)', border: '1px solid var(--c-divider)', borderRadius: 'var(--r-md)', padding: '12px 14px' }}>
                  <div style={{ fontWeight: 700, fontSize: '13px', color: 'var(--c-navy)', marginBottom: '3px' }}>{gap}</div>
                  <div style={{ fontSize: '12px', color: 'var(--c-text-secondary)', lineHeight: 1.5 }}>{desc}</div>
                </div>
              ))}
            </div>
          </div>

          {/* ── Meet Team HackManthan ── */}
          <div style={{ marginTop: '48px', marginBottom: '24px', width: '100%' }}>
            <h2 style={{
              fontSize: '28px',
              fontWeight: 700,
              color: 'var(--c-navy)',
              textAlign: 'center',
              margin: '0 0 28px',
              letterSpacing: '-0.01em',
            }}>
              Meet Team HackManthan
            </h2>

            <div className="team-grid">
              {teamMembers.map((member) => (
                <div
                  key={member.name}
                  style={{
                    background: '#FFFFFF',
                    border: '1px solid #D8E0EA',
                    borderRadius: '8px',
                    padding: '24px 12px 20px',
                    textAlign: 'center',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    boxShadow: '0 1px 3px rgba(11, 42, 91, 0.04)',
                  }}
                >
                  <div style={{
                    width: '100px',
                    height: '100px',
                    borderRadius: '50%',
                    overflow: 'hidden',
                    marginBottom: '16px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    flexShrink: 0,
                    background: '#F4F7FA',
                  }}>
                    <img
                      src={member.photo}
                      alt={member.name}
                      style={{
                        width: '100%',
                        height: '100%',
                        objectFit: 'contain',
                        display: 'block',
                      }}
                    />
                  </div>

                  <div style={{
                    fontSize: '14px',
                    fontWeight: 700,
                    color: 'var(--c-navy)',
                    marginBottom: '4px',
                    lineHeight: 1.3,
                  }}>
                    {member.name}
                  </div>

                  <div style={{
                    fontSize: '11px',
                    color: 'var(--c-text-muted)',
                    lineHeight: 1.4,
                    marginBottom: '16px',
                    minHeight: '32px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    flexGrow: 1,
                  }}>
                    {member.role}
                  </div>

                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '10px',
                    marginTop: 'auto',
                  }}>
                    <a
                      href={member.linkedin}
                      target="_blank"
                      rel="noopener noreferrer"
                      aria-label={`${member.name} LinkedIn`}
                      style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        padding: '2px',
                      }}
                    >
                      <img
                        src="/team/linkedin.png"
                        alt="LinkedIn"
                        width="16"
                        height="16"
                        style={{ display: 'block' }}
                      />
                    </a>
                    {member.github ? (
                      <a
                        href={member.github}
                        target="_blank"
                        rel="noopener noreferrer"
                        aria-label={`${member.name} GitHub`}
                        style={{
                          display: 'inline-flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          padding: '2px',
                        }}
                      >
                        <img
                          src="/team/github.png"
                          alt="GitHub"
                          width="16"
                          height="16"
                          style={{ display: 'block' }}
                        />
                      </a>
                    ) : (
                      <span
                        aria-hidden="true"
                        style={{
                          display: 'inline-flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          padding: '2px',
                          opacity: 0.35,
                          cursor: 'default',
                        }}
                      >
                        <img
                          src="/team/github.png"
                          alt="GitHub"
                          width="16"
                          height="16"
                          style={{ display: 'block' }}
                        />
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>
    </main>
  );
};

export default AboutPage;
