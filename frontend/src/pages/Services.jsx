import React from "react";
import { Box, Typography, Link } from "@mui/material";
import ArrowForwardIcon from "@mui/icons-material/ArrowForward";

const services = [
    {
        id: 1,
        title: "Financial Planning",
        description:
            "Vanguard offers personalized financial planning services to help you achieve your financial goals. Their advisors provide guidance on budgeting, saving, investing, and retirement planning.",
        link: "https://investor.vanguard.com/advice/personal-financial-advisor",
    },
    {
        id: 2,
        title: "Retirement Planning",
        description:
            "Vanguard provides comprehensive retirement planning services, including strategies for saving, investing, and managing your retirement income. They help you maximize your Social Security benefits and plan for healthcare costs in retirement.",
        link: "https://investor.vanguard.com/investor-resources-education/retirement",
    },
    {
        id: 3,
        title: "Investment Management",
        description:
            "Vanguard's investment management services include building a diversified portfolio tailored to your financial situation, risk tolerance, and investment goals. They offer a range of low-cost mutual funds and ETFs.",
        link: "https://investor.vanguard.com/advice",
    },
    {
        id: 4,
        title: "Wealth Management",
        description:
            "For high-net-worth clients, Vanguard offers personalized wealth management services. Their advisors help you preserve and grow your wealth through holistic financial planning, investment advisory services, and estate planning.",
        link: "https://investor.vanguard.com/wealth-management/personal-advisor-wealth-management",
    },
    {
        id: 5,
        title: "Self-Managed",
        description:
            "Vanguard also supports self-managed investors by providing tools and resources to help you manage your investments independently. They offer a variety of investment options and educational resources to empower you to make informed decisions.",
        link: "https://www.vanguard.com/",
    },
];
const Services = () => {
    return (
        <Box
            sx={{
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                marginTop: "64px",
                padding: "16px",
                width: "100%",
            }}
        >
            <Typography
                variant="h4"
                component="h4"
                sx={{
                    marginBottom: "10px",
                    fontWeight: "bold",
                    fontSize: "40px",
                }}
            >
                Our Financial Services
            </Typography>
            <Typography
                variant="h6"
                component="h6"
                sx={{ marginBottom: "60px" }}
            >
                Comprehensive financial solutions tailored to your unique needs
            </Typography>
            {services.map((service) => (
                <Box
                    key={service.id}
                    sx={{
                        border: "1px solid #ccc",
                        borderRadius: "8px",
                        padding: "20px",
                        marginBottom: "20px",
                        boxShadow: "0 4px 6px rgba(0, 0, 0, 0.1)",
                        transition: "box-shadow 0.3s ease",
                        width: "800px",
                        height: "210px",
                        "&:hover": {
                            boxShadow: "0 8px 16px rgba(0, 0, 0, 0.2)",
                        },
                    }}
                >
                    <Typography variant="h5" component="h3">
                        {service.title}
                    </Typography>
                    <Typography variant="body1" sx={{ mt: 2 }}>
                        {service.description}
                    </Typography>
                    <Link
                        href={service.link}
                        target="_blank"
                        sx={{
                            display: "block",
                            marginTop: "8px",
                            color: "#0073e6",
                            textDecoration: "none",
                            position: "relative",
                            left: "23px",
                            "&:hover": {
                                textDecoration: "underline",
                            },
                        }}
                    >
                        <ArrowForwardIcon
                            sx={{
                                fontSize: "24px",
                                marginLeft: "4px",
                                position: "absolute",
                                left: "-30px",
                            }}
                        />
                        {`Learn more`}
                    </Link>
                </Box>
            ))}
        </Box>
    );
};
export default Services;
