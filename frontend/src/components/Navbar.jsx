import React from "react";
import AppBar from "@mui/material/AppBar";
import Toolbar from "@mui/material/Toolbar";
import Typography from "@mui/material/Typography";
import Button from "@mui/material/Button";
import Box from "@mui/material/Box";
import { Container } from "@mui/material";
import { Link, Route, Routes } from "react-router-dom";

const Navbar = () => {
    const menuItems = [
        { page: "Dashboard", route: "/dashboard" },
        { page: "Services", route: "/services" },
        { page: "Transactions", route: "/transactions" },
        { page: "FAQ", route: "https://support.vanguard.com/" },
        { page: "Education", route: "https://investor.vanguard.com/investor-resources-education" },
        { page: "Account", route: "/account" },
    ];

    return (
        <AppBar
            position="sticky"
            sx={{ width: "100%", backgroundColor: "background.default" }}
        >
            <Container>
                <Toolbar
                    sx={{
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                    }}
                >
                    <img
                        src="/vanguard-typogrophy.png"
                        alt="Vanguard Logo"
                        style={{
                            height: "75px",
                            maxWidth: "200px",
                            objectFit: "contain",
                        }}
                    />

                    <Box sx={{ display: "flex", flexWrap: "wrap", gap: 2 }}>
                        {menuItems.map((item, index) => (
                            <Button key={`${item}-${index}`} color="primary">
                                <Link
                                    to={item.route}
                                    style={{
                                        textDecoration: "none",
                                        color: "inherit",
                                    }}
                                >
                                    {item.page}
                                </Link>
                            </Button>
                        ))}
                    </Box>
                </Toolbar>
            </Container>
        </AppBar>
    );
};

export default Navbar;
