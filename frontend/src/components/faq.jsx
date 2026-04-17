import './faq.css';
import ophiuchus_logo from '../assets/ophiuchus_logo.svg'

function FAQ() {

    const getReference = (reference) => {
        const urlMap = {
            "Reference: Government of Canada (2018)": "https://www.canada.ca/en/health-canada/services/drugs-health-products/veterinary-drugs/antimicrobial-resistance/oversight-quality-active-pharmaceutical-ingredients-veterinary-use.html",
            "Reference: Katrime Integrated Health (2022)": "https://nccid.ca/publications/glossary-terms-antimicrobial-resistance/",
            "Reference: World Health Organization (2019)": "https://www.who.int/publications/i/item/9789241515481",
            "Reference: National Antimicrobial Resistance Monitoring System for Enteric Bacteria (NARMS) (2024)": "https://www.cdc.gov/narms/glossary/index.html",
            "Reference: AMR Dictionary (2020)": "https://www.amrdictionary.net/contents/image/AMR%20dictionary%20Englilsh%20version%201.2.pdf",
            "Reference: Harrison, P.F & Lederberg J. (1998)": "https://pubmed.ncbi.nlm.nih.gov/23035315/"
        }
        return urlMap[reference] || "";
    };

    const sampleQA = [

        {
            question: "What are Active Pharmaceutical Ingredients?",
            answer: "The biologically active ingredients in a pharmaceutical drug.",
            other_term: "Other Term/s: APIs, API, active ingredients, pharmaceutical actives",
            reference: "Reference: Government of Canada (2018)"
        },
        {
            question: "What is Antimicrobial Stewardship?",
            answer: "Coordinated interventions designed to promote, improve, monitor, and evaluate the judicious use of antimicrobials so as to preserve their future effectiveness and to promote and protect human and animal health.",
            other_term: "Other Term/s: AMS, antimicrobial stewardship program, antibiotic stewardship",
            reference: "Reference: Katrime Integrated Health (2022)"
        },
        {
            question: "What is Antimicrobial Resistance?",
            answer: "Microorganisms such as bacteria, fungi, viruses and parasites change when exposed to antimicrobial drugs such as antibiotics (antibacterials), antifungals, antivirals, antimalarials and anthelmintics. As a result, the medicines become ineffective.",
            other_term: "Other Term/s: AMR, drug resistance, antibiotic-resistant",
            reference: "Reference: World Health Organization (2019)"
        },
        {
            question: "What is Antibiotic?",
            answer: "A drug that kills or stops the growth of bacteria. Antibiotics are a type of antimicrobial. Penicillin and ciprofloxacin are examples of antibiotics.",
            other_term: "Other Term/s: antibacterial",
            reference: "Reference: National Antimicrobial Resistance Monitoring System for Enteric Bacteria (NARMS) (2024)"
        },
        {
            question: "What is Antimicrobial?",
            answer: "A substance that kills or stops the growth of microbes, including bacteria, fungi, or viruses. Antimicrobial agents are grouped according to the microbes they act against (antibiotics [bacteria], antifungals [fungi], and antivirals [viruses]). Also referred to as drugs.",
            reference: "Reference: National Antimicrobial Resistance Monitoring System for Enteric Bacteria (NARMS) (2024)"
        },
        {
            question: "What are Microbes?",
            answer: "Living organisms, like bacteria, fungi, or viruses, which can cause infections or disease. Also referred to as germs.",
            reference: "Reference: National Antimicrobial Resistance Monitoring System for Enteric Bacteria (NARMS) (2024)"
        },
        {
            question: "What is Antibiogram?",
            answer: "A laboratory resource used to determine the sensitivity of a bacterial strain to different antibiotics. A cumulative antibiogram provides a profile of antibacterial susceptibilities within an institution or aggregation of institutions over a given period time to monitor trends in antibacterial resistance and to guide empirical antibacterial therapy selection.",
            reference: "Reference: Katrime Integrated Health (2022)"
        },
        {
            question: "What is Nosocomial Infection?",
            answer: "An infection acquired in the hospital, excluding infections incubating at time of admission.",
            other_term: "Other Term/s: Healthcare associated infection (HAI), Hospital-acquired infection",
            reference: "Reference: Katrime Integrated Health (2022)"
        },
        {
            question: "What is Empirical Antibiotic Treatment?",
            answer: "Initial antibiotic treatment targeted at the most probable causative microorganism. The recommendations should be based on local susceptibility data, available scientific evidence or expert opinion, when evidence is lacking.",
            other_term: "Other Term/s: empirical therapy, empirical treatment",
            reference: "Reference: World Health Organization (2019)"
        },
        {
            question: "What is Optimal Duration Treatment?",
            answer: "The ideal length of time for treatment with antimicrobials to prevent disease relapse and antimicrobial resistance, and also to ensure patient safety and cost-effectiveness.",
            reference: "Reference: Katrime Integrated Health (2022)"
        },
        {
            question: "What is Superbug?",
            answer: "A strain or type of bacterium that has become resistant to the majority of current antibiotics.",
            reference: "Reference: AMR Dictionary (2020)"
        },
        {
            question: "What is Responsible Use?",
            answer: "This term implies that activities and capabilities of human and animal health systems are aligned to ensure that patients receive the right treatment at the right time, use these drugs appropriately, and benefit from them.",
            other_term: "Other Term/s: Rational antimicrobial use, Prudent use, Judicial use",
            reference: "Reference: Katrime Integrated Health (2022)"
        },
        {
            question: "What is Defined Daily Dose (DDD)?",
            answer: "Assumed average maintenance dose per day for a drug used for its main indication in its target species.",
            reference: "Reference: Katrime Integrated Health (2022)"
        },
        {
            question: "What is Selective pressure?",
            answer: "A driving force of evolution and natural selection, selective pressure is any phenomena which alters the reproductive behavior and fitness of living organisms within their environment. Antimicrobial-use creates a strong selective pressure as microbes that are able to survive despite antimicrobial treatment can proliferate and extend their reproductive advantage within the microbial community.",
            other_term: "Other Term/s: Squeezing the balloon",
            reference: "Reference: Katrime Integrated Health (2022)"
        },
        {
            question: "What is Combination Therapy?",
            answer: "Treatment involving more than one drug. A rationale for use of combination therapy has been the lesser likelihood that a pathogen develops resistance to multiple drugs.",
            reference: "Reference: Katrime Integrated Health (2022)"
        },
        {
            question: "What is Antibiotic Misuse?",
            answer: "The inappropriate or, improper overuse of antibiotics, often without medical justification, with potentially serious negative effects on health.",
            other_term: "Other Term/s: inappropriate use, unneccessary use",
            reference: "Reference: AMR Dictionary (2020)"
        },
        {
            question: "What is Multidrug Resistance?",
            answer: "Resistant to more than one type of antimicrobial, whether antibiotics, antivirals, antifungal, or antiparasitic drugs; thus, few or no effective treatments are available for MDR infections.",
            other_term: "Other Term/s: MDR",
            reference: "Reference: AMR Dictionary (2020)"
        },
        {
            question: "What is Antibiotic Prophylaxis?",
            answer: "Administration of antibiotics before evidence of infection, that is intended to ward off disease.",
            other_term: "Other Term/s: Prophylactic antibiotic therapy, prophylaxis",
            reference: "Reference: Harrison, P.F & Lederberg J. (1998)"
        },
        {
            question: "What is Resistome?",
            answer: "The reservoir of all types of antibiotic resistance genes (acquired or intrinsic), their precursors, and potential resistance mechanisms that directly or indirectly result in resistance.",
            reference: "Reference: Katrime Integrated Health (2022)"
        },
        {
            question: "What is Antimicrobial time-out?",
            answer: "An active reassessment of an antimicrobial prescription 48–72 hours after first administration to allow medical staff to take into account laboratory culture and susceptibility testing results and the patient’s response to therapy and current condition.",
            reference: "Reference: National Antimicrobial Resistance Monitoring System for Enteric Bacteria (NARMS) (2024)"
        }
    ];

    return (
        <>
            <div className="header">
                <img src={ophiuchus_logo} className="" alt="Ophiuchus logo" />
                    <div className="title-container">
                    <p className="title">FAQs</p>
                    <p className="sub-title">Find answers to common questions</p>
                    </div>
            </div>

            <div className="faq-container">
                <div className="cards-container">
                    {sampleQA.map((item, index) => {
                        const referenceUrl = getReference(item.reference);
                        
                        return (
                            <div className="qa-card" key={index}>
                                <div className="card-question">
                                    <h3>{item.question}</h3>
                                </div>
                                <div className="card-answer">
                                    <p>{item.answer}</p>
                                </div>
                                <div className="card-term">
                                    <p>{item.other_term}</p>
                                </div>
                                <div className="card-reference">
                                    {referenceUrl ? (
                                        <p>
                                            <a 
                                                href={referenceUrl} 
                                                target="_blank" 
                                                rel="noopener noreferrer"
                                                className="reference-link"
                                            >
                                                {item.reference}
                                            </a>
                                        </p>
                                    ) : (
                                        <p>{item.reference}</p>
                                    )}
                                </div>
                            </div>

                        );
                    })}
                </div>
            </div>
        </>
    );
}

export default FAQ;