import { ComponentFixture, TestBed } from '@angular/core/testing';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { Grades } from './grades';

describe('Grades', () => {
  let component: Grades;
  let fixture: ComponentFixture<Grades>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        Grades,
        HttpClientTestingModule
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(Grades);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
