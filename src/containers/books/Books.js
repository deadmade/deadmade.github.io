import React, { Component } from "react";
import "./Books.css";
import { Slide } from "react-awesome-reveal";
import { books } from "../../portfolio";
import BookCard from "../../components/bookCard/BookCard";

class Books extends Component {
  render() {
    const theme = this.props.theme;
    return (
      <div className="main" id="certs">
        <div className="books-header-div">
          <Slide direction="up" duration={2000} triggerOnce>
            <h1 className="books-header" style={{ color: theme.text }}>
              Bücher
            </h1>
          </Slide>
        </div>
        <div className="books-body-div">
          {books.books.map((book) => {
            return <BookCard book={book} theme={theme} />;
          })}
        </div>
      </div>
    );
  }
}

export default Books;
