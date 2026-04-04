import './about.css';
import ophiuchus_logo from '../assets/ophiuchus_logo.svg'

function About() {
    const sampleQA = [

        {
            question: "The standard Lorem Ipsum passage, used since the 1500s",
            answer: "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur."
        },
        {
            question: "The standard Lorem Ipsum passage, used since the 1500s",
            answer: "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur."
        },
        {
            question: "The standard Lorem Ipsum passage, used since the 1500s",
            answer: "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur."
        },
        {
            question: "The standard Lorem Ipsum passage, used since the 1500s",
            answer: "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur."
        },
        {
            question: "The standard Lorem Ipsum passage, used since the 1500s",
            answer: "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur."
        }
    ];

    return (
        <>

            <div className="header">
                <img src={ophiuchus_logo} className="" alt="Ophiuchus logo" />
                    <div className="title-container">
                    <p className="title">About</p>
                    <p className="sub-title">Learn more about Ophiuchus</p>
                    </div>
            </div>

            <div className="about-container">
                <div className="cards-container">
                    {sampleQA.map((item, index) => (
                        <div className="qa-card" key={index}>
                            <div className="card-question">
                                <h3>{item.question}</h3>
                            </div>
                            <div className="card-answer">
                                <p>{item.answer}</p>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </>
    );
}

export default About;